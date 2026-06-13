---
name: fastapi-patterns
description: FastAPI architecture patterns, REST API design, dependency injection, async patterns, middleware. Use for Python FastAPI backend work.
origin: local
---

# FastAPI Development Patterns

FastAPI 아키텍처 및 API 패턴 — 확장 가능한 프로덕션 등급 비동기 서비스.

## When to Activate

- FastAPI로 REST API 구축
- router → service → repository 레이어 구조화
- SQLAlchemy 비동기 DB, 캐싱, 백그라운드 태스크 설정
- 검증, 예외 처리, 페이지네이션 추가
- 환경별 설정 관리

## REST API Structure

```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("", response_model=list[OrderResponse])
async def list_orders(
    page: int = 0,
    size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return await OrderService(db).list(current_user.id, offset=page*size, limit=size)

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    body: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return await OrderService(db).create(current_user.id, body)

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return await OrderService(db).get_by_id(current_user.id, order_id)
```

## Dependency Injection

```python
# app/core/deps.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

engine = create_async_engine(settings.DATABASE_URL, pool_size=10, max_overflow=20)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

## Background Tasks

```python
from fastapi import BackgroundTasks

@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    body: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    user = await UserService(db).create(body)
    background_tasks.add_task(send_welcome_email, user.email)
    return user
```

## Middleware

```python
# app/main.py
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.monotonic()
    response = await call_next(request)
    process_time = time.monotonic() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## 앱 생성 (main.py)

```python
from fastapi import FastAPI
from app.api.v1.router import router as v1_router
from app.exceptions import AppException, app_exception_handler

app = FastAPI(title="My API", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, ...)
app.add_exception_handler(AppException, app_exception_handler)
app.include_router(v1_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
```
