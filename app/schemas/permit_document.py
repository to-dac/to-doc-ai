# 인허가 문서 자동작성 요청/응답 스키마 — 필지·세션 기반으로 양식 질문을 채운다
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.permit_chat import LandContext


class ApplicablePermit(BaseModel):
    """필지에 적용 가능한 인허가(템플릿) 후보."""

    model_config = ConfigDict(extra="ignore")

    id: int | None = Field(default=None, description="후보 식별자")
    templateCode: str | None = Field(default=None, description="양식 코드")
    name: str | None = Field(default=None, description="인허가명")
    description: str | None = Field(default=None, description="설명")


class LandInfo(LandContext):
    """문서작성용 필지 정보. LandContext 에 적용 가능 인허가 목록을 더한다."""

    applicablePermits: list[ApplicablePermit] = Field(
        default_factory=list, description="적용 가능 인허가 후보"
    )


class Question(BaseModel):
    """양식의 단일 질문 항목."""

    model_config = ConfigDict(extra="ignore")

    id: int = Field(description="질문 식별자")
    layoutKey: str | None = Field(default=None, description="레이아웃 키")
    questionType: str | None = Field(default=None, description="질문 유형(TEXT/RADIO 등)")
    displayType: str | None = Field(default=None, description="표시 유형")
    name: str | None = Field(default=None, description="질문명")
    description: str | None = Field(default=None, description="질문 설명")
    options: str | None = Field(default=None, description="선택지(JSON 문자열)")
    validation: str | None = Field(default=None, description="검증 규칙(JSON 문자열)")
    subFields: Any = Field(default=None, description="하위 필드")
    metadata: Any = Field(default=None, description="메타데이터")
    orderNo: int | None = Field(default=None, description="표시 순서")


class Section(BaseModel):
    """질문 묶음(섹션)."""

    model_config = ConfigDict(extra="ignore")

    id: int = Field(description="섹션 식별자")
    sectionCode: str | None = Field(default=None, description="섹션 코드")
    name: str | None = Field(default=None, description="섹션명")
    orderNo: int | None = Field(default=None, description="표시 순서")
    questions: list[Question] = Field(default_factory=list, description="질문 목록")


class DocumentTemplate(BaseModel):
    """인허가 문서 양식."""

    model_config = ConfigDict(extra="ignore")

    id: int | None = Field(default=None, description="양식 식별자")
    templateCode: str | None = Field(default=None, description="양식 코드")
    name: str | None = Field(default=None, description="양식명")
    description: str | None = Field(default=None, description="양식 설명")
    version: str | None = Field(default=None, description="버전")
    metadata: Any = Field(default=None, description="메타데이터")
    sections: list[Section] = Field(default_factory=list, description="섹션 목록")


class FilledQuestion(Question):
    """채워진 질문 — 원본 질문에 answer/source 를 더한다."""

    answer: str | None = Field(default=None, description="채워진 답변(없으면 null)")
    source: str = Field(default="unknown", description="근거 출처: land_info/conversation/unknown")


class FilledSection(BaseModel):
    """채워진 섹션."""

    id: int
    sectionCode: str | None = None
    name: str | None = None
    orderNo: int | None = None
    questions: list[FilledQuestion] = Field(default_factory=list)


class PermitDocumentRequest(BaseModel):
    """문서 자동작성 요청.

    land_info(필지 데이터)와 template(양식)을 기본 근거로, thread_id 가 있으면
    해당 세션 대화 이력을 보조 근거로 삼아 각 질문을 채운다.
    """

    thread_id: str | None = Field(default=None, description="대화 이력 보강용 세션 식별자")
    land_info: LandInfo = Field(description="필지 데이터(채우기 1차 근거)")
    template: DocumentTemplate = Field(description="채울 양식")


class PermitDocumentResponse(BaseModel):
    """문서 자동작성 응답 — 채워진 양식."""

    thread_id: str | None = Field(default=None, description="요청에 사용된 세션 식별자")
    templateCode: str | None = Field(default=None, description="양식 코드")
    sections: list[FilledSection] = Field(default_factory=list, description="채워진 섹션 목록")
    filled_count: int = Field(description="채워진(answer 있는) 질문 수")
    total_count: int = Field(description="전체 질문 수")
