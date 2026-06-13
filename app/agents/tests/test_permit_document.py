# 문서 자동작성 로직 단위 테스트 — LLM/세션 호출은 mock, 채우기·검증만 검증
from types import SimpleNamespace

import pytest

from app.agents import permit_document
from app.agents.permit_document import (
    _AnswerItem,
    _build_extraction_prompt,
    _coerce_answer,
    _conversation_transcript,
    _ExtractionResult,
    fill_permit_document,
)
from app.schemas.permit_document import (
    DocumentTemplate,
    PermitDocumentRequest,
    Question,
)


def _radio_q() -> Question:
    return Question(
        id=112,
        questionType="RADIO",
        name="신청 구분",
        options='["대수선","용도변경","대수선 및 용도변경"]',
        validation='{"required": true}',
    )


def test_coerce_answer_accepts_valid_option():
    answer, source = _coerce_answer(_radio_q(), "용도변경", "conversation")
    assert answer == "용도변경"
    assert source == "conversation"


def test_coerce_answer_rejects_out_of_options():
    """선택지 밖의 값은 null + unknown 으로 강등."""
    answer, source = _coerce_answer(_radio_q(), "신축", "conversation")
    assert answer is None
    assert source == "unknown"


def test_coerce_answer_rejects_maxlength_violation():
    q = Question(id=1, questionType="TEXT", name="성명", validation='{"maxLength": 3}')
    answer, source = _coerce_answer(q, "홍길동입니다", "land_info")
    assert answer is None
    assert source == "unknown"


def test_coerce_answer_none_value_is_unknown():
    answer, source = _coerce_answer(Question(id=1), None, "land_info")
    assert answer is None
    assert source == "unknown"


def test_coerce_answer_keeps_generated_source():
    """generate_missing 모드의 임의 생성 값은 source='generated' 로 유지된다."""
    answer, source = _coerce_answer(Question(id=1, questionType="TEXT"), "임의값", "generated")
    assert answer == "임의값"
    assert source == "generated"


def test_extraction_prompt_strict_vs_generate():
    """generate_missing 플래그가 프롬프트 규칙을 전환한다."""
    qs = [Question(id=1, name="성명")]
    strict = _build_extraction_prompt({}, "", qs)
    generate = _build_extraction_prompt({}, "", qs, generate_missing=True)

    assert "추측 금지" in strict
    assert "generated" not in strict
    assert "임의로 생성" in generate
    assert 'source="generated"' in generate


def test_conversation_transcript_keeps_human_and_ai():
    messages = [
        SimpleNamespace(type="human", content="대수선 하려고요"),
        SimpleNamespace(type="ai", content="건축허가가 필요합니다"),
        SimpleNamespace(type="tool", content="무시되는 도구 메시지"),
    ]
    text = _conversation_transcript(messages)
    assert "사용자: 대수선 하려고요" in text
    assert "비서: 건축허가가 필요합니다" in text
    assert "도구" not in text


@pytest.mark.asyncio
async def test_fill_permit_document_maps_answers(monkeypatch):
    """추출 결과가 템플릿에 병합되고 filled_count 가 집계된다(agent=None, LLM mock)."""
    template = DocumentTemplate(
        id=1,
        templateCode="tc",
        sections=[
            {
                "id": 10,
                "questions": [
                    {"id": 101, "questionType": "TEXT", "name": "대지 위치"},
                    {"id": 102, "questionType": "TEXT", "name": "신청인 성명"},
                ],
            }
        ],
    )
    body = PermitDocumentRequest(
        land_info={"pnu": "1", "address": "서울 강남구 삼성동 1"},
        template=template,
    )

    async def fake_extract(land_info, transcript, questions, **_):
        assert land_info["pnu"] == "1"
        return _ExtractionResult(
            answers=[
                _AnswerItem(question_id=101, value="서울 강남구 삼성동 1", source="land_info"),
                _AnswerItem(question_id=102, value=None, source="unknown"),
            ]
        )

    monkeypatch.setattr(permit_document, "_extract_answers", fake_extract)

    result = await fill_permit_document(None, body)

    assert result.templateCode == "tc"
    assert result.total_count == 2
    assert result.filled_count == 1
    q101 = result.sections[0].questions[0]
    assert q101.answer == "서울 강남구 삼성동 1"
    assert q101.source == "land_info"
    assert result.sections[0].questions[1].answer is None


@pytest.mark.asyncio
async def test_fill_permit_document_loads_template_by_permit_type(monkeypatch):
    """template 없이 permit_type 만 주면 서류 정보 문서에서 양식을 로드해 채운다."""
    captured: dict = {}

    async def fake_extract(land_info, transcript, questions, **_):
        captured["question_count"] = len(questions)
        return _ExtractionResult(answers=[])

    monkeypatch.setattr(permit_document, "_extract_answers", fake_extract)

    body = PermitDocumentRequest(land_info={"pnu": "1"}, permit_type="mountain")
    result = await fill_permit_document(None, body)

    assert result.templateCode == "mountain_permit"
    assert result.total_count == captured["question_count"] > 0


def test_request_requires_template_or_permit_type():
    """template·permit_type 둘 다 없으면 검증 단계에서 거부된다."""
    with pytest.raises(ValueError):
        PermitDocumentRequest(land_info={"pnu": "1"})


@pytest.mark.asyncio
async def test_fill_permit_document_pulls_conversation(monkeypatch):
    """thread_id 가 있으면 agent.aget_state 로 대화 이력을 읽어 추출에 넘긴다."""
    captured: dict = {}

    class FakeAgent:
        async def aget_state(self, config):
            captured["config"] = config
            return SimpleNamespace(
                values={"messages": [SimpleNamespace(type="human", content="대수선 할게요")]}
            )

    async def fake_extract(land_info, transcript, questions, **_):
        captured["transcript"] = transcript
        return _ExtractionResult(answers=[])

    monkeypatch.setattr(permit_document, "_extract_answers", fake_extract)

    body = PermitDocumentRequest(
        thread_id="t-1",
        land_info={"pnu": "1"},
        template=DocumentTemplate(sections=[]),
    )
    await fill_permit_document(FakeAgent(), body)

    assert captured["config"]["configurable"]["thread_id"] == "t-1"
    assert "사용자: 대수선 할게요" in captured["transcript"]
