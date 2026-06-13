---
paths:
  - "**/tests/**/*.py"
  - "**/conftest.py"
---
# 테스트 패턴

## conftest.py 기본 픽스처

```python
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
```

## pyproject.toml 설정

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

## Anthropic API Mock

```python
async def test_run_agent_returns_result(client: AsyncClient, mocker):
    mock_create = mocker.patch("app.agents.base.anthropic.AsyncAnthropic")
    mock_instance = mock_create.return_value
    mock_instance.messages.create = mocker.AsyncMock(
        return_value=mocker.Mock(
            content=[mocker.Mock(text="응답 텍스트")]
        )
    )

    response = await client.post("/api/v1/agent/run", json={"prompt": "안녕"})
    assert response.status_code == 200
    assert response.json()["result"] == "응답 텍스트"
```

## MCP 툴 Mock

```python
async def test_mcp_tool_called(mocker):
    mock_server = mocker.AsyncMock()
    mock_server.list_tools.return_value = [{"name": "my_tool", "description": "..."}]

    mocker.patch("app.mcp.servers.registry.MCP_SERVERS", [mock_server])

    from app.mcp.client import MCPClientManager
    manager = MCPClientManager()
    tools = await manager.get_tools()
    assert len(tools) == 1
```

## 테스트 이름 패턴

```python
# 좋음
async def test_run_agent_returns_200():
async def test_run_agent_without_prompt_returns_422():
async def test_mcp_server_failure_is_skipped():

# 나쁨
async def test_agent():
async def test_api():
```

## API 테스트 예시

```python
async def test_run_agent_returns_200(client: AsyncClient, mocker):
    mocker.patch("app.agents.base.MCPClientManager.get_tools", return_value=[])
    mocker.patch(
        "app.agents.base.anthropic.AsyncAnthropic.messages.create",
        ...
    )
    response = await client.post("/api/v1/agent/run", json={"prompt": "테스트"})
    assert response.status_code == 200
```

## 금지 사항

- 실제 Anthropic API 호출 (비용 발생, 네트워크 의존)
- `asyncio.sleep()` 남용
- 테스트 간 모듈 상태 공유
