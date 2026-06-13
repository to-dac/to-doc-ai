# to-dac-backend

FastAPI 기반 백엔드 서버. Anthropic Claude를 에이전트로 활용하며 MCP 서버를 통해 툴을 연동합니다.

## 프로젝트 구조

```
to-dac-backend/
├── app/
│   ├── main.py               # FastAPI entrypoint
│   ├── core/
│   │   ├── config.py         # 환경변수 설정 (pydantic-settings)
│   │   └── logging.py        # 로깅 초기화
│   ├── api/
│   │   └── v1/
│   │       ├── router.py     # v1 라우터 통합
│   │       └── endpoints/
│   │           └── agent.py  # POST /api/v1/agent/run
│   ├── agents/
│   │   └── base.py           # AgentRunner — Claude + MCP 툴 실행
│   ├── mcp/
│   │   ├── client.py         # MCPClientManager — 서버 통합 관리
│   │   └── servers/
│   │       ├── base.py       # BaseMCPServer 추상 클래스
│   │       └── registry.py   # MCP 서버 등록 목록
│   └── schemas/
│       └── agent.py          # AgentRequest / AgentResponse
├── tests/
├── pyproject.toml
└── .env.example
```

## 시작하기

### 1. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일에서 `ANTHROPIC_API_KEY`를 입력합니다.

### 2. 의존성 설치

```bash
uv sync --group dev
```

### 3. 서버 실행

```bash
uv run uvicorn app.main:app --reload
```

서버가 `http://localhost:8000`에서 시작됩니다.  
API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

## MCP 서버 추가

`app/mcp/servers/` 아래에 `BaseMCPServer`를 구현한 클래스를 만들고, `registry.py`의 `MCP_SERVERS` 리스트에 등록합니다.

```python
# app/mcp/servers/my_server.py
from app.mcp.servers.base import BaseMCPServer

class MyMCPServer(BaseMCPServer):
    name = "my-server"

    async def list_tools(self):
        return [{"name": "my_tool", "description": "...", "input_schema": {...}}]

    async def call_tool(self, tool_name, tool_input):
        ...
```

```python
# app/mcp/servers/registry.py
from app.mcp.servers.my_server import MyMCPServer

MCP_SERVERS = [MyMCPServer()]
```

## 개발

```bash
# 테스트 실행
uv run pytest

# 린트 / 포맷
uv run ruff check .
uv run ruff format .

# 패키지 추가
uv add <패키지명>
uv add --group dev <패키지명>
```

## API

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 헬스체크 |
| POST | `/api/v1/agent/run` | 에이전트 실행 |

### POST /api/v1/agent/run

**Request**
```json
{
  "prompt": "작업 내용을 입력하세요",
  "session_id": "optional-session-id"
}
```

**Response**
```json
{
  "result": "에이전트 응답",
  "session_id": null
}
```
