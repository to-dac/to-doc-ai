# 인허가 멀티턴 대화용 커스텀 도구 — 확정 유형을 대화 상태에 기록한다
from __future__ import annotations

from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.types import Command

from app.agents.permits import PERMITS_BY_CODE, get_permit


@tool
def set_permit_type(code: str, runtime: ToolRuntime) -> Command:
    """사용자와의 대화로 확정된 인허가 유형을 대화 상태(permit_type)에 기록한다.

    이후 턴에서는 이 값이 유지되므로 유형을 다시 묻지 말고 같은 문서로 이어서 답하라.

    Args:
        code: 인허가 유형 코드. building, mountain, farmland, road, river, dev_act 중 하나.
    """
    permit = get_permit(code)
    if permit is None:
        valid = ", ".join(PERMITS_BY_CODE)
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        f"Error: 미등록 인허가 유형 '{code}'. 가능한 코드: {valid}",
                        tool_call_id=runtime.tool_call_id,
                        status="error",
                    )
                ]
            }
        )

    return Command(
        update={
            "permit_type": permit.code.value,
            "messages": [
                ToolMessage(
                    f"인허가 유형 확정: {permit.name} ({permit.code.value}). "
                    f"문서 경로: {permit.doc_path}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
