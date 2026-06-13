# 인허가 멀티턴 대화 요청/응답 스키마
from pydantic import BaseModel, ConfigDict, Field


class BuildingInfo(BaseModel):
    """필지 위 건물 정보. 값이 없을 수 있어 전 필드 선택적."""

    model_config = ConfigDict(extra="ignore")

    hasBuilding: bool | None = Field(default=None, description="건물 존재 여부")
    bldNm: str | None = Field(default=None, description="건물명")
    mainPurpsCdNm: str | None = Field(default=None, description="주용도")
    etcPurps: str | None = Field(default=None, description="기타용도")
    platArea: float | None = Field(default=None, description="대지면적(㎡)")
    archArea: float | None = Field(default=None, description="건축면적(㎡)")
    totArea: float | None = Field(default=None, description="연면적(㎡)")
    bcRat: float | None = Field(default=None, description="건폐율(%)")
    vlRat: float | None = Field(default=None, description="용적률(%)")
    heit: float | None = Field(default=None, description="높이(m)")
    grndFlrCnt: int | None = Field(default=None, description="지상층수")
    ugrndFlrCnt: int | None = Field(default=None, description="지하층수")
    useAprDay: str | None = Field(default=None, description="사용승인일")
    strctCdNm: str | None = Field(default=None, description="구조")


class LandUseItem(BaseModel):
    """지역지구 등 토지이용 규제 항목."""

    model_config = ConfigDict(extra="ignore")

    code: str | None = Field(default=None, description="지역지구코드")
    name: str | None = Field(default=None, description="지역지구명")
    conflictType: str | None = Field(default=None, description="저촉/포함 등 관계")


class LandContext(BaseModel):
    """대상 필지의 토지특성·건물·규제 데이터. 첫 턴에만 전달하면 세션에 보존된다."""

    model_config = ConfigDict(extra="ignore")

    pnu: str | None = Field(default=None, description="필지고유번호(PNU)")
    address: str | None = Field(default=None, description="주소")
    ldCodeNm: str | None = Field(default=None, description="법정동명")
    lndcgrCodeNm: str | None = Field(default=None, description="지목")
    lndpclAr: str | None = Field(default=None, description="대지면적(㎡)")
    oficlLndpcl: str | None = Field(default=None, description="공시지가 기준 면적")
    prposArea1Nm: str | None = Field(default=None, description="용도지역1")
    prposArea2Nm: str | None = Field(default=None, description="용도지역2")
    ladUseSittnNm: str | None = Field(default=None, description="토지이용상황")
    tpgrphHgCodeNm: str | None = Field(default=None, description="지형높이")
    tpgrphFrmCodeNm: str | None = Field(default=None, description="지형형상")
    roadSideCodeNm: str | None = Field(default=None, description="도로접면")
    pblntfPclnd: str | None = Field(default=None, description="개별공시지가(원/㎡)")
    lastUpdtDt: str | None = Field(default=None, description="최종갱신일")
    building: BuildingInfo | None = Field(default=None, description="건물 정보")
    landUses: list[LandUseItem] = Field(default_factory=list, description="토지이용 규제 목록")


class PermitChatRequest(BaseModel):
    """인허가 대화 한 턴 요청.

    thread_id 를 생략하면 서버가 새 세션을 발급한다. 같은 thread_id 로 다시
    호출하면 직전 대화가 이어진다(멀티턴).

    land_context 는 첫 턴에만 보내면 세션에 보존되어, 이후 턴에서 생략해도
    에이전트가 동일 필지 정보를 근거로 답한다.
    """

    message: str = Field(min_length=1, description="사용자 발화")
    thread_id: str | None = Field(default=None, description="세션 식별자. 미지정 시 신규 발급")
    land_context: LandContext | None = Field(
        default=None, description="대상 필지 정보. 첫 턴에만 전달하면 세션에 보존된다."
    )


class PermitChatResponse(BaseModel):
    """인허가 대화 한 턴 응답."""

    thread_id: str = Field(description="이 대화의 세션 식별자(다음 턴에 재사용)")
    reply: str = Field(description="에이전트 응답 텍스트")
    permit_type: str | None = Field(default=None, description="현재 세션에서 확정된 인허가 유형 코드")
