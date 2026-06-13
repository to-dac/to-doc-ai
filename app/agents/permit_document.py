# 인허가 문서 자동작성 로직 — 필지·대화 근거로 양식 질문을 채운다(A1: 채팅 에이전트는 읽기만)
from __future__ import annotations

import json
import logging

from pydantic import BaseModel, Field

from app.agents.llm import build_model
from app.schemas.permit_document import (
    FilledQuestion,
    FilledSection,
    PermitDocumentRequest,
    PermitDocumentResponse,
    Question,
)

logger = logging.getLogger(__name__)

# 추출 모델이 반환할 고정 스키마. 템플릿이 동적이라 question_id 로 매핑한다.
_VALID_SOURCES = {"land_info", "conversation", "unknown"}


class _AnswerItem(BaseModel):
    """질문 1개에 대한 추출 결과."""

    question_id: int = Field(description="대상 질문 id")
    value: str | None = Field(default=None, description="채운 값(근거 없으면 null)")
    source: str = Field(default="unknown", description="land_info/conversation/unknown")


class _ExtractionResult(BaseModel):
    """추출 모델의 구조화 출력."""

    answers: list[_AnswerItem] = Field(default_factory=list)


def _conversation_transcript(messages: list) -> str:
    """체크포인터에서 읽은 메시지들을 사람이 읽을 수 있는 대화 텍스트로 요약한다.

    도구 호출/시스템 잡음은 제외하고 user/assistant 발화 위주로 추린다.
    """
    lines: list[str] = []
    for msg in messages or []:
        msg_type = getattr(msg, "type", None)
        content = getattr(msg, "content", None)
        if not content or not isinstance(content, str):
            continue
        if msg_type == "human":
            lines.append(f"사용자: {content}")
        elif msg_type == "ai":
            lines.append(f"비서: {content}")
    return "\n".join(lines)


async def _collect_conversation(agent, thread_id: str | None) -> str:
    """thread_id 세션의 대화 이력을 조회한다(읽기 전용). 실패/부재 시 빈 문자열."""
    if agent is None or not thread_id:
        return ""
    try:
        snapshot = await agent.aget_state({"configurable": {"thread_id": thread_id}})
    except Exception:
        logger.warning("세션 상태 조회 실패 — 대화 보강 없이 진행 (thread_id=%s)", thread_id)
        return ""
    values = getattr(snapshot, "values", None) or {}
    return _conversation_transcript(values.get("messages", []))


def _iter_questions(template) -> list[Question]:
    """템플릿의 모든 섹션 질문을 평탄화한다."""
    return [q for section in template.sections for q in section.questions]


def _build_extraction_prompt(land_info: dict, transcript: str, questions: list[Question]) -> str:
    """추출 모델에 줄 프롬프트를 만든다."""
    q_lines = []
    for q in questions:
        parts = [f"- id={q.id}", f"name={q.name!r}"]
        if q.questionType:
            parts.append(f"type={q.questionType}")
        if q.description:
            parts.append(f"설명={q.description!r}")
        if q.options:
            parts.append(f"선택지={q.options}")
        if q.validation:
            parts.append(f"검증={q.validation}")
        q_lines.append(" | ".join(parts))

    conversation_block = transcript or "(대화 이력 없음)"
    return f"""너는 인허가 신청서 자동작성 도우미다. 아래 근거로 각 질문의 답을 채워라.

[필지 정보(JSON)]
{json.dumps(land_info, ensure_ascii=False)}

[대화 이력]
{conversation_block}

[채울 질문 목록]
{chr(10).join(q_lines)}

[규칙]
- 각 질문 id 에 대해 value 를 채운다. 근거가 없으면 value=null.
- 선택지(options)가 있으면 반드시 그 중 하나만 고른다(JSON 배열). 애매하면 null.
- 추측 금지. 필지/대화에 근거가 있을 때만 채운다.
- source 는 값의 출처: 필지에서 왔으면 "land_info", 대화에서 왔으면 "conversation", 못 채웠으면 "unknown".
- 모든 질문에 대해 한 개씩 answers 항목을 반환한다."""


async def _extract_answers(
    land_info: dict, transcript: str, questions: list[Question]
) -> _ExtractionResult:
    """LLM 경계 — 구조화 출력으로 질문별 답을 추출한다.

    이 함수만 모델을 호출하므로, 테스트에서는 이 함수를 대체(monkeypatch)한다.
    """
    model = build_model()
    structured = model.with_structured_output(_ExtractionResult)
    prompt = _build_extraction_prompt(land_info, transcript, questions)
    return await structured.ainvoke(prompt)


def _coerce_answer(question: Question, value: str | None, source: str) -> tuple[str | None, str]:
    """추출된 값을 질문 제약(options·validation)으로 검증한다. 위반 시 (None, "unknown")."""
    if value is None or value == "":
        return None, "unknown"

    source = source if source in _VALID_SOURCES else "unknown"

    # 선택지 제약: options 안의 값만 허용.
    if question.options:
        try:
            choices = json.loads(question.options)
        except (json.JSONDecodeError, TypeError):
            choices = None
        if isinstance(choices, list) and value not in choices:
            return None, "unknown"

    # 검증 규칙: maxLength 초과 시 무효.
    if question.validation:
        try:
            rules = json.loads(question.validation)
        except (json.JSONDecodeError, TypeError):
            rules = {}
        max_length = rules.get("maxLength") if isinstance(rules, dict) else None
        if isinstance(max_length, int) and len(value) > max_length:
            return None, "unknown"

    return value, source


async def fill_permit_document(agent, body: PermitDocumentRequest) -> PermitDocumentResponse:
    """필지·세션 근거로 양식 질문을 채워 응답을 만든다.

    - agent 는 세션 대화 이력 조회(읽기)에만 쓰인다. None 이면 필지만으로 채운다.
    - 실제 채우기는 별도 모델 호출(_extract_answers)로 수행한다(채팅 스레드 미오염).
    """
    transcript = await _collect_conversation(agent, body.thread_id)
    land_info = body.land_info.model_dump()
    questions = _iter_questions(body.template)

    extraction = await _extract_answers(land_info, transcript, questions)
    by_id = {a.question_id: a for a in extraction.answers}

    filled_count = 0
    filled_sections: list[FilledSection] = []
    for section in body.template.sections:
        filled_questions: list[FilledQuestion] = []
        for q in section.questions:
            item = by_id.get(q.id)
            answer, source = (
                _coerce_answer(q, item.value, item.source) if item else (None, "unknown")
            )
            if answer is not None:
                filled_count += 1
            filled_questions.append(
                FilledQuestion(**q.model_dump(), answer=answer, source=source)
            )
        filled_sections.append(
            FilledSection(
                id=section.id,
                sectionCode=section.sectionCode,
                name=section.name,
                orderNo=section.orderNo,
                questions=filled_questions,
            )
        )

    return PermitDocumentResponse(
        thread_id=body.thread_id,
        templateCode=body.template.templateCode,
        sections=filled_sections,
        filled_count=filled_count,
        total_count=len(questions),
    )
