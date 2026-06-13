# 인허가 멀티턴 대화 에이전트 — docs/ 문서에 직접 접근해 질문에 근거 기반으로 답한다
from __future__ import annotations

import asyncio
import logging

from deepagents import create_deep_agent
from deepagents.backends.composite import CompositeBackend
from deepagents.backends.filesystem import FilesystemBackend
from deepagents.backends.state import StateBackend
from langgraph.checkpoint.memory import InMemorySaver

from app.agents.llm import build_model
from app.agents.permits import DOCS_DIR, DOCS_MOUNT, build_docs_index
from app.agents.state import ConversationState
from app.agents.tools import set_permit_type

logger = logging.getLogger(__name__)


def _system_prompt() -> str:
    """인허가 문서 인덱스를 주입한 시스템 프롬프트를 만든다.

    전체 문서를 미리 싣지 않고 인덱스(유형·경로)만 노출한다. 실제 내용은
    필요한 턴에 read_file/grep 으로 직접 읽어 근거로 삼는다.
    """
    return f"""너는 토지 인허가 안내 비서다. 한국어로 간결하고 정확하게 답한다.

{DOCS_MOUNT} 디렉토리에 인허가 유형별 '체크리스트 서류'와 '처리 프로세스'를 담은
마크다운 문서가 있다. 아래는 그 인덱스다(전체 내용 아님).

[인허가 문서 인덱스]
{build_docs_index()}

[작업 방식 — 반드시 준수]
1) 사용자 질문의 의도와 키워드로 인허가 유형을 좁혀라.
   - 후보가 여러 개로 모호하면, 후보를 제시하고 한 가지로 확정하는 질문을 먼저 하라.
   - 단정할 수 있으면 곧장 진행하라.
2) 유형이 확정되면 set_permit_type(code) 도구를 호출해 대화 상태에 기록하라.
3) 그 다음, 해당 유형의 문서 경로를 read_file 로 직접 읽어
   '## 체크리스트 서류'와 '## 처리 프로세스' 원문을 근거로 답하라.
   - "필요 서류만" 같은 부분 질문은 grep 으로 '- [ ]' 항목만 추려도 된다.
   - 문서에 없는 내용은 추측하지 말고 "문서에 명시되어 있지 않다"고 답하라.
4) 이전 턴에서 이미 유형이 확정된 상태(permit_type)면 다시 묻지 말고
   같은 문서로 이어서 답하라. 사용자가 다른 유형으로 바꾸면 그때 갱신하라.
5) 인덱스에 없는 유형을 물으면, 지원 목록을 안내하고 가장 가까운 유형을 제안하라."""


def build_permit_agent():
    """docs 파일시스템 + 멀티턴 체크포인터를 갖춘 인허가 대화 에이전트를 생성한다.

    - CompositeBackend: 기본 StateBackend(대화 상태) + /docs(읽기용 FilesystemBackend).
    - InMemorySaver: thread_id 별 대화 상태를 프로세스 메모리에 보존(멀티턴).

    앱 기동 시 1회 호출해 재사용해야 InMemorySaver 가 턴 간 유지된다.
    """
    backend = CompositeBackend(
        default=StateBackend(),
        routes={
            f"{DOCS_MOUNT}/": FilesystemBackend(root_dir=DOCS_DIR, virtual_mode=True),
        },
    )
    return create_deep_agent(
        model=build_model(),
        backend=backend,
        checkpointer=InMemorySaver(),
        state_schema=ConversationState,
        tools=[set_permit_type],
        system_prompt=_system_prompt(),
    )


async def run_permit_chat(agent, prompt: str, thread_id: str) -> tuple[str, str | None]:
    """단일 발화를 실행하고 (응답 텍스트, 확정 인허가 유형)을 반환한다.

    동일 thread_id 로 호출하면 이전 턴 상태(대화 이력·permit_type)가 이어진다.
    """
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": prompt}]},
        config={"configurable": {"thread_id": thread_id}},
    )
    return result["messages"][-1].content, result.get("permit_type")


async def run_permit_turn(agent, prompt: str, session_id: str) -> str:
    """run_permit_chat 의 텍스트만 반환하는 래퍼(데모·하위호환용)."""
    reply, _ = await run_permit_chat(agent, prompt, session_id)
    return reply


async def _demo() -> None:
    """간단한 멀티턴 데모: 같은 session_id 로 두 턴을 이어 실행한다."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    agent = build_permit_agent()
    session_id = "demo-session"

    for turn in ("농지에 건물을 지으려면 어떤 허가가 필요하고 서류는 뭐가 필요해?", "그럼 처리 절차는?"):
        logger.info("\n>>> 사용자: %s", turn)
        answer = await run_permit_turn(agent, turn, session_id)
        logger.info(">>> 에이전트:\n%s", answer)


if __name__ == "__main__":
    asyncio.run(_demo())
