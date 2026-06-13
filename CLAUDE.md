# CLAUDE.md

Python/FastAPI 백엔드 API 프로젝트를 위한 Claude Code 가이드.

## 프로젝트 개요

**to-dac-backend** — FastAPI 기반 AI Agent 백엔드 서비스.

Anthropic Claude API를 호출하는 AgentRunner와 MCP(Model Context Protocol) 서버를 통합 관리하는 MCPClientManager로 구성된다. 클라이언트는 `/api/v1/agent/run` 엔드포인트로 프롬프트를 전달하면, Agent가 MCP 툴을 사용해 응답을 생성한다.

**기술 스택**
- FastAPI 0.115+ / Pydantic v2 / pydantic-settings
- Anthropic SDK (`claude-sonnet-4-6`)
- httpx (비동기 HTTP 클라이언트)
- pytest-asyncio / ruff
- **DB 없음** — 상태는 Anthropic 세션 ID로 관리

## 실행 명령어

```bash
# 개발 서버
uvicorn app.main:app --reload

# 테스트
pytest                                  # 전체 테스트
pytest -x                               # 첫 실패에서 중단
pytest --cov=app --cov-report=html      # 커버리지 리포트

# 린트 & 포맷
ruff check .                            # 린트
ruff format .                           # 포맷
```

## 아키텍처

```
Router  →  AgentRunner  →  MCPClientManager  →  MCP Servers
 (HTTP)    (Anthropic)      (Tool 통합)          (외부 툴)
```

```
app/
├── api/             # FastAPI 라우터 (엔드포인트, 입력 검증)
│   └── v1/
│       ├── router.py
│       └── endpoints/
│           └── agent.py     # POST /agent/run
├── agents/          # AI Agent 실행 로직
│   └── base.py      # AgentRunner — Anthropic API 호출
├── mcp/             # MCP 서버 관리
│   ├── client.py    # MCPClientManager — 툴 통합
│   └── servers/
│       ├── base.py      # BaseMCPServer (ABC)
│       └── registry.py  # MCP_SERVERS 목록
├── schemas/         # Pydantic 스키마 (요청/응답)
│   └── agent.py     # AgentRequest, AgentResponse
├── core/            # 설정, 로깅
│   ├── config.py    # Settings (pydantic-settings)
│   └── logging.py
└── main.py

tests/
├── api/             # 엔드포인트 테스트 (AsyncClient)
├── agents/          # AgentRunner 단위 테스트 (mocker)
└── conftest.py      # 픽스처
```

## 개발 워크플로우

```
1. 기능 계획   → /dev plan  (코드베이스 분석 후 계획서 작성)
2. 구현 & 검증 → /dev run   (계획서 기반 구현 + 린트 확인)
3. 테스트      → /dev test  (TDD 워크플로우, 테스트 먼저 작성)
4. 리뷰        → /dev review (로컬 변경 또는 PR 종합 리뷰)
5. 커밋        → /git commit
6. PR 생성     → /git pr
```

전체 파이프라인 한 번에: `/dev`

## 슬래시 커맨드

### dev — 개발 워크플로우

| 커맨드 | 설명 |
|--------|------|
| `/dev` | 계획 → 구현 → 테스트 전체 워크플로우 |
| `/dev init` | 프로젝트 분석 후 CLAUDE.md·rules 자동 커스터마이징 |
| `/dev plan` | 코드베이스 분석 후 구현 계획서 작성 |
| `/dev run` | 계획서 기반 코드 구현 및 검증 |
| `/dev test` | TDD 워크플로우 (테스트 먼저 작성) |
| `/dev review` | 로컬 변경(Python 특화) 또는 PR 종합 리뷰 |
| `/dev build` | 린트·타입 오류 진단 및 수정 |
| `/dev fix` | 린트·타입 에러 자동 수정 |
| `/dev verify` | 린트·타입체크·테스트·커버리지·보안 전체 검증 |
| `/dev coverage` | 커버리지 분석 및 미달 영역 테스트 생성 |

### git — GitHub 워크플로우

| 커맨드 | 설명 |
|--------|------|
| `/git commit` | 변경사항 커밋 |
| `/git pr` | PR 자동 생성 (push → PR → CI 확인) |
| `/git issue` | 이슈 생성 (`bug` / `feat`) |

## 에이전트

| 에이전트 | 용도 | 언제 사용 |
|---------|------|----------|
| `code-reviewer` | Python/FastAPI 코드 리뷰 | 코드 수정 후 항상 |
| `python-build-resolver` | 린트·타입·임포트 에러 수정 | 검증 실패 시 |
| `security-reviewer` | 보안 취약점 분석 | API 키·입력처리 변경 시 |
| `tdd-guide` | TDD 워크플로우 안내 | 새 기능/버그수정 시 |
| `planner` | 기능 구현 계획 수립 | 복잡한 기능 시작 전 |
| `python-performance-reviewer` | 비동기 성능 분석 | AgentRunner·MCP 성능 이슈 시 |

## 핵심 규칙

1. **코드 수정 후**: 반드시 `code-reviewer` 에이전트 실행
2. **새 기능**: TDD 워크플로우 준수 (테스트 RED → 구현 GREEN → 리팩토링)
3. **린트 실패**: `python-build-resolver` 에이전트 사용, 경고 억제 금지
4. **API 키 노출**: `ANTHROPIC_API_KEY`는 반드시 환경변수로 — 코드에 하드코딩 금지
5. **커밋 전**: `ruff check . && pytest` 통과 확인
6. **MCP 서버 추가**: `registry.py`의 `MCP_SERVERS` 목록에만 등록

## 스킬 참조

| 작업 | 스킬 |
|------|------|
| REST API 구조 설계 | `fastapi-patterns` |
| 보안 설정 (API 키 관리) | `fastapi-security` |
| TDD 패턴 | `fastapi-tdd` |
| 코딩 표준 (PEP 8, 타입힌트) | `python-coding-standards` |
| REST API 설계 원칙 | `api-design` |
| Claude API 사용법 | `claude-api` |
| ADR 작성 | `architecture-decision-records` |
