# 인허가 멀티턴 대화 요청/응답 스키마
from pydantic import BaseModel, Field


class PermitChatRequest(BaseModel):
    """인허가 대화 한 턴 요청.

    thread_id 를 생략하면 서버가 새 세션을 발급한다. 같은 thread_id 로 다시
    호출하면 직전 대화가 이어진다(멀티턴).
    """

    message: str = Field(min_length=1, description="사용자 발화")
    thread_id: str | None = Field(default=None, description="세션 식별자. 미지정 시 신규 발급")


class PermitChatResponse(BaseModel):
    """인허가 대화 한 턴 응답."""

    thread_id: str = Field(description="이 대화의 세션 식별자(다음 턴에 재사용)")
    reply: str = Field(description="에이전트 응답 텍스트")
    permit_type: str | None = Field(default=None, description="현재 세션에서 확정된 인허가 유형 코드")
