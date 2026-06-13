# 멀티턴 대화 상태 — DeepAgentState 를 확장해 확정된 인허가 유형을 턴 간 보존한다
from __future__ import annotations

from deepagents import DeepAgentState


class ConversationState(DeepAgentState):
    """인허가 멀티턴 대화 상태.

    DeepAgentState(messages·todos·files)에 permit_type 을 추가한다.
    InMemorySaver + thread_id 로 체크포인트되어 다음 턴에서 재사용된다.
    """

    # 확정된 인허가 유형 코드. 미확정이면 키가 없거나 None.
    permit_type: str | None

    # 대상 필지 정보(첫 턴에 전달받아 보존). 미전달이면 키가 없거나 None.
    land_context: dict | None
