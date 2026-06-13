# /api/v1/permit/chat 멀티턴 엔드포인트 테스트 — 실제 LLM 호출 없이 thread_id 배선만 검증
import pytest
from fastapi.testclient import TestClient

from app.api.v1.endpoints import permit_chat as endpoint
from app.main import app

client = TestClient(app)


@pytest.fixture
def fake_agent(monkeypatch):
    """app.state 에 sentinel 에이전트를 주입하고, run_permit_chat 호출을 기록한다."""
    calls: list[tuple[object, str, str, dict | None]] = []

    async def fake_run(agent, message, thread_id, land_context=None):
        calls.append((agent, message, thread_id, land_context))
        return f"reply to: {message}", "farmland"

    sentinel = object()
    app.state.permit_agent = sentinel
    monkeypatch.setattr(endpoint, "run_permit_chat", fake_run)
    yield sentinel, calls
    app.state.permit_agent = None


def test_chat_issues_thread_id_when_missing(fake_agent):
    """thread_id 미지정 시 서버가 발급해 응답에 담는다."""
    _, calls = fake_agent
    res = client.post("/api/v1/permit/chat", json={"message": "농지전용 서류 알려줘"})
    assert res.status_code == 200
    body = res.json()
    assert body["thread_id"]  # 비어있지 않음
    assert body["reply"] == "reply to: 농지전용 서류 알려줘"
    assert body["permit_type"] == "farmland"
    # 발급된 thread_id 가 에이전트 호출에 그대로 전달됐는지
    assert calls[0][2] == body["thread_id"]


def test_chat_reuses_same_thread_id_across_turns(fake_agent):
    """같은 thread_id 로 두 턴을 호출하면 동일 세션 키로 이어진다."""
    _, calls = fake_agent
    tid = "session-123"
    client.post("/api/v1/permit/chat", json={"message": "1턴", "thread_id": tid})
    res2 = client.post("/api/v1/permit/chat", json={"message": "2턴", "thread_id": tid})
    assert res2.json()["thread_id"] == tid
    assert [c[2] for c in calls] == [tid, tid]
    assert [c[1] for c in calls] == ["1턴", "2턴"]


def test_chat_returns_503_when_agent_uninitialized(monkeypatch):
    """에이전트가 초기화되지 않았으면 503 을 반환한다."""
    app.state.permit_agent = None
    res = client.post("/api/v1/permit/chat", json={"message": "안녕"})
    assert res.status_code == 503


def test_chat_rejects_empty_message(fake_agent):
    """빈 메시지는 422 검증 오류."""
    res = client.post("/api/v1/permit/chat", json={"message": ""})
    assert res.status_code == 422


def test_chat_passes_land_context_on_first_turn(fake_agent):
    """첫 턴의 land_context 가 dict 로 변환되어 run_permit_chat 에 전달된다."""
    _, calls = fake_agent
    res = client.post(
        "/api/v1/permit/chat",
        json={
            "message": "이 땅에 증축 가능해?",
            "land_context": {
                "pnu": "1168010100107370000",
                "prposArea1Nm": "일반상업지역",
                "building": {"hasBuilding": True, "bcRat": 42.5677},
                "landUses": [{"code": "UQA220", "name": "일반상업지역", "conflictType": "포함"}],
            },
        },
    )
    assert res.status_code == 200
    land_context = calls[0][3]
    assert land_context is not None
    assert land_context["pnu"] == "1168010100107370000"
    assert land_context["building"]["bcRat"] == 42.5677
    assert land_context["landUses"][0]["code"] == "UQA220"


def test_chat_land_context_omitted_passes_none(fake_agent):
    """land_context 를 생략하면 None 으로 전달된다(이후 턴)."""
    _, calls = fake_agent
    client.post("/api/v1/permit/chat", json={"message": "그럼 서류는?", "thread_id": "t-1"})
    assert calls[0][3] is None
