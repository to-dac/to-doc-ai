# 인허가 문서 자동작성 엔드포인트 — 필지·세션 근거로 양식 질문을 채워 반환한다
from fastapi import APIRouter, Request

from app.agents.permit_document import fill_permit_document
from app.schemas.permit_document import PermitDocumentRequest, PermitDocumentResponse

router = APIRouter()


@router.post(
    "/document",
    response_model=PermitDocumentResponse,
    summary="필지·세션 기반 인허가 문서 자동작성",
)
async def permit_document(body: PermitDocumentRequest, request: Request) -> PermitDocumentResponse:
    """land_info(필지)와 template(양식)으로 질문을 채운다.

    thread_id 가 있으면 해당 세션 대화 이력을 보조 근거로 활용한다. 세션이 없거나
    에이전트가 미초기화여도 필지 정보만으로 동작한다(읽기 실패는 무시).
    """
    agent = getattr(request.app.state, "permit_agent", None)
    return await fill_permit_document(agent, body)
