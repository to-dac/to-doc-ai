# 인허가 멀티턴 에이전트 단위 테스트 — 네트워크 호출 없이 배선·문서접근만 검증한다
from types import SimpleNamespace

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app.agents import permit_agent
from app.agents.permits import (
    DOCS_DIR,
    DOCS_MOUNT,
    PERMITS,
    build_docs_index,
    get_permit,
)
from app.agents.state import ConversationState
from app.agents.tools import set_permit_type


def test_all_permits_map_to_existing_files() -> None:
    """등록된 6개 유형이 모두 docs/ 실제 파일과 1:1로 매칭된다."""
    assert len(PERMITS) == 6
    missing = [p.filename for p in PERMITS if not (DOCS_DIR / p.filename).exists()]
    assert missing == []


def test_doc_path_uses_mount_prefix() -> None:
    farm = get_permit("farmland")
    assert farm is not None
    assert farm.doc_path == f"{DOCS_MOUNT}/{farm.filename}"


def test_docs_index_lists_all_codes() -> None:
    index = build_docs_index()
    for permit in PERMITS:
        assert permit.code.value in index
        assert permit.doc_path in index


def test_get_permit_unknown_returns_none() -> None:
    assert get_permit("unknown_code") is None


def test_set_permit_type_records_state() -> None:
    """확정 유형 코드는 Command 로 permit_type 상태를 갱신한다."""
    runtime = SimpleNamespace(tool_call_id="call-1")
    result = set_permit_type.func(code="farmland", runtime=runtime)
    assert isinstance(result, Command)
    assert result.update["permit_type"] == "farmland"


def test_set_permit_type_rejects_unknown_code() -> None:
    """미등록 코드는 상태를 바꾸지 않고 에러 ToolMessage 만 반환한다."""
    runtime = SimpleNamespace(tool_call_id="call-2")
    result = set_permit_type.func(code="nope", runtime=runtime)
    assert isinstance(result, Command)
    assert "permit_type" not in result.update
    assert result.update["messages"][0].status == "error"


def test_backend_exposes_six_docs() -> None:
    """CompositeBackend 의 /docs 라우트가 6개 마크다운을 노출한다."""
    from deepagents.backends.composite import CompositeBackend
    from deepagents.backends.filesystem import FilesystemBackend
    from deepagents.backends.state import StateBackend

    backend = CompositeBackend(
        default=StateBackend(),
        routes={f"{DOCS_MOUNT}/": FilesystemBackend(root_dir=DOCS_DIR, virtual_mode=True)},
    )
    entries = backend.ls(f"{DOCS_MOUNT}/").entries
    md_files = [e for e in entries if not e["is_dir"] and e["path"].endswith(".md")]
    assert len(md_files) == 6


def test_build_permit_agent_wires_multiturn(monkeypatch) -> None:
    """backend(Composite)·checkpointer(InMemorySaver)·state_schema·도구 배선을 검증한다."""
    captured: dict = {}

    def fake_create_deep_agent(**kwargs):
        captured.update(kwargs)
        return "AGENT"

    monkeypatch.setattr(permit_agent, "build_model", lambda: "MODEL")
    monkeypatch.setattr(permit_agent, "create_deep_agent", fake_create_deep_agent)

    agent = permit_agent.build_permit_agent()

    assert agent == "AGENT"
    assert isinstance(captured["checkpointer"], InMemorySaver)
    assert captured["state_schema"] is ConversationState
    assert set_permit_type in captured["tools"]
    # /docs 라우트가 backend 에 마운트되어 있어야 한다.
    assert f"{DOCS_MOUNT}/" in captured["backend"].routes
