---
paths:
  - "**/api/**/*.py"
  - "**/endpoints/**/*.py"
---
# Router 패턴

## 실제 구조 (agent 엔드포인트 기준)

```python
from fastapi import APIRouter, HTTPException

from app.agents.base import AgentRunner
from app.schemas.agent import AgentRequest, AgentResponse

router = APIRouter()


@router.post("/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    try:
        runner = AgentRunner()
        result = await runner.run(request.prompt, request.session_id)
        return AgentResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 규칙

- `response_model` 항상 명시 — 응답 필드 노출 제어
- 라우터는 AgentRunner로 즉시 위임 — Anthropic API 직접 호출 금지
- 각 도메인 라우터는 `router.py`에서 prefix와 tags를 지정해 등록

## 라우터 등록 (api/v1/router.py)

```python
from fastapi import APIRouter
from app.api.v1.endpoints import agent

router = APIRouter()
router.include_router(agent.router, prefix="/agent", tags=["agent"])
```

## 새 도메인 추가 패턴

```python
# app/api/v1/endpoints/foo.py
router = APIRouter()

@router.post("/run", response_model=FooResponse)
async def run_foo(request: FooRequest):
    runner = FooRunner()
    result = await runner.run(request.prompt)
    return FooResponse(result=result)
```

```python
# app/api/v1/router.py 에 추가
from app.api.v1.endpoints import agent, foo
router.include_router(foo.router, prefix="/foo", tags=["foo"])
```
