---
paths:
  - "**/*.py"
---
# Architecture

AI Agent + MCP 통합 아키텍처.

```
Router  →  AgentRunner  →  MCPClientManager  →  MCP Servers
 (HTTP)    (Anthropic)      (Tool 통합)          (외부 툴)
```

```
app/
├── api/
│   └── v1/
│       ├── router.py            # 라우터 통합
│       └── endpoints/
│           └── agent.py         # POST /agent/run
├── agents/
│   └── base.py                  # AgentRunner — Anthropic API 호출
├── mcp/
│   ├── client.py                # MCPClientManager — 툴 통합
│   └── servers/
│       ├── base.py              # BaseMCPServer (ABC)
│       └── registry.py          # MCP_SERVERS 목록 (여기에만 등록)
├── schemas/
│   └── agent.py                 # AgentRequest, AgentResponse
├── core/
│   ├── config.py                # Settings (pydantic-settings)
│   └── logging.py
└── main.py                      # FastAPI 앱, 라우터 등록
```

## 레이어 책임

| 레이어 | 책임 | 금지 사항 |
|--------|------|----------|
| Router (endpoints/) | HTTP 매핑, 입력 검증, 응답 포맷 | 비즈니스 로직, AgentRunner 직접 설정 |
| AgentRunner (agents/) | Anthropic API 호출, 툴 루프 실행 | HTTP 객체 참조 |
| MCPClientManager (mcp/) | MCP 서버 툴 조회·실행 | Anthropic API 직접 호출 |
| BaseMCPServer (mcp/servers/) | 특정 MCP 서버 어댑터 구현 | 비즈니스 로직 |

## MCP 서버 추가 방법

`BaseMCPServer`를 상속하여 `list_tools()`와 `call_tool()`을 구현한 뒤 `registry.py`의 `MCP_SERVERS`에 등록한다. 다른 파일은 수정하지 않는다.
