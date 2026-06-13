# 인허가 멀티턴 대화 엔드포인트 — thread_id 로 세션을 구분해 대화를 이어간다
import uuid

from fastapi import APIRouter, HTTPException, Request

from app.agents.permit_agent import run_permit_chat
from app.schemas.permit_chat import PermitChatRequest, PermitChatResponse

router = APIRouter()


@router.post("/chat", response_model=PermitChatResponse, summary="인허가 멀티턴 대화")
async def permit_chat(body: PermitChatRequest, request: Request) -> PermitChatResponse:
    """한 턴의 인허가 대화를 처리한다.

    thread_id 가 없으면 새로 발급해 응답에 담아 반환한다. 클라이언트는 이후
    같은 thread_id 를 보내 같은 세션의 대화를 이어간다.
    """
    agent = getattr(request.app.state, "permit_agent", None)
    if agent is None:
        raise HTTPException(status_code=503, detail="인허가 에이전트가 초기화되지 않았습니다.")

    thread_id = body.thread_id or str(uuid.uuid4())
    reply, permit_type = await run_permit_chat(agent, body.message, thread_id)
    return PermitChatResponse(thread_id=thread_id, reply=reply, permit_type=permit_type)
