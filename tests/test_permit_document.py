# /api/v1/permit/document 엔드포인트 테스트 — LLM 호출 없이 배선·검증만 확인
import pytest
from fastapi.testclient import TestClient

from app.api.v1.endpoints import permit_document as endpoint
from app.main import app

client = TestClient(app)


def _template() -> dict:
    return {
        "id": 1,
        "templateCode": "building_major_repair_use_change_permit",
        "name": "건축물 대수선·용도변경 허가",
        "sections": [
            {
                "id": 10,
                "sectionCode": "applicant_info",
                "name": "신청인 정보",
                "orderNo": 1,
                "questions": [
                    {
                        "id": 101,
                        "layoutKey": "land_address",
                        "questionType": "TEXT",
                        "name": "대지 위치",
                        "validation": '{"required": true}',
                        "orderNo": 1,
                    }
                ],
            }
        ],
    }


@pytest.fixture
def fake_fill(monkeypatch):
    """fill_permit_document 호출을 가로채 인자를 기록하고 고정 응답을 반환한다."""
    calls: list[tuple[object, object]] = []

    async def fake(agent, body):
        calls.append((agent, body))
        from app.schemas.permit_document import (
            FilledQuestion,
            FilledSection,
            PermitDocumentResponse,
        )

        return PermitDocumentResponse(
            thread_id=body.thread_id,
            templateCode=body.template.templateCode,
            sections=[
                FilledSection(
                    id=10,
                    questions=[
                        FilledQuestion(id=101, answer="서울특별시 강남구 삼성동 1", source="land_info")
                    ],
                )
            ],
            filled_count=1,
            total_count=1,
        )

    monkeypatch.setattr(endpoint, "fill_permit_document", fake)
    return calls


def test_document_fills_and_returns(fake_fill):
    """정상 요청 시 채워진 양식을 반환하고 land_info 가 전달된다."""
    res = client.post(
        "/api/v1/permit/document",
        json={
            "thread_id": "123",
            "land_info": {"pnu": "1168010100100010000", "address": "서울특별시 강남구 삼성동 1"},
            "template": _template(),
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["templateCode"] == "building_major_repair_use_change_permit"
    assert body["filled_count"] == 1
    assert body["sections"][0]["questions"][0]["answer"] == "서울특별시 강남구 삼성동 1"
    # land_info 가 스키마로 파싱되어 전달됐는지
    _, passed = fake_fill[0]
    assert passed.land_info.pnu == "1168010100100010000"


def test_document_works_without_thread_id(fake_fill):
    """thread_id 없이 land_info 만으로도 200."""
    res = client.post(
        "/api/v1/permit/document",
        json={"land_info": {"pnu": "1"}, "template": _template()},
    )
    assert res.status_code == 200
    assert fake_fill[0][1].thread_id is None


def test_document_requires_land_info():
    """land_info 누락은 422."""
    res = client.post("/api/v1/permit/document", json={"template": _template()})
    assert res.status_code == 422


def test_document_requires_template():
    """template 누락은 422."""
    res = client.post("/api/v1/permit/document", json={"land_info": {"pnu": "1"}})
    assert res.status_code == 422
