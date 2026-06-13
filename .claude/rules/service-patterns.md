---
paths:
  - "**/agents/**/*.py"
  - "**/mcp/**/*.py"
---
# Agent / MCP 패턴

## AgentRunner 구조

```python
import uuid
from typing import Optional

import anthropic

from app.core.config import settings
from app.mcp.client import MCPClientManager


class AgentRunner:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.mcp_manager = MCPClientManager()

    async def run(self, prompt: str, session_id: Optional[str] = None) -> str:
        if session_id is None:
            session_id = str(uuid.uuid4())

        tools = await self.mcp_manager.get_tools()

        response = await self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            tools=tools,
            messages=[{"role": "user", "content": prompt}],
        )

        return self._extract_text(response)
```

## MCP 서버 구현 패턴

```python
from typing import Any
from app.mcp.servers.base import BaseMCPServer


class MyMCPServer(BaseMCPServer):
    name = "my-server"

    async def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "my_tool",
                "description": "툴 설명",
                "input_schema": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            }
        ]

    async def call_tool(self, tool_name: str, tool_input: dict[str, Any]) -> Any:
        if tool_name == "my_tool":
            return {"result": f"처리됨: {tool_input['query']}"}
        raise ValueError(f"Unknown tool: {tool_name}")
```

```python
# app/mcp/servers/registry.py — 여기에만 등록
from app.mcp.servers.my_server import MyMCPServer

MCP_SERVERS = [MyMCPServer()]
```

## 규칙

- AgentRunner는 `anthropic.AsyncAnthropic` 인스턴스를 생성자에서 초기화
- API 키는 반드시 `settings.ANTHROPIC_API_KEY`에서 읽음 — 하드코딩 금지
- MCP 서버 추가 시 `registry.py`만 수정
- `list_tools()` 실패는 경고 로그로 처리 (MCPClientManager 내장)
