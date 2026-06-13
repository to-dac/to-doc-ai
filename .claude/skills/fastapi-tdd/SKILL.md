---
name: fastapi-tdd
description: FastAPI TDD patterns — pytest-asyncio, async test client, fixture design, mocking. Use for writing tests.
origin: local
---

# FastAPI TDD Patterns

## 핵심 의존성

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.coverage.run]
source = ["app"]
omit = ["app/main.py", "*/migrations/*"]
```

```
pytest
pytest-asyncio
httpx
pytest-mock
pytest-cov
```

## conftest.py 전체 예시

```python
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.core.deps import get_db
from app.models.base import Base

TEST_DB_URL = "postgresql+asyncpg://user:pass@localhost/test_db"

@pytest_asyncio.fixture(scope="session")
async def engine():
    e = create_async_engine(TEST_DB_URL)
    async with e.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield e
    async with e.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await e.dispose()

@pytest_asyncio.fixture
async def db(engine):
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        async with session.begin():
            yield session
            await session.rollback()

@pytest_asyncio.fixture
async def client(db):
    async def override():
        yield db
    app.dependency_overrides[get_db] = override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def auth_client(client, db):
    # 테스트 사용자 생성 및 토큰 발급
    from app.core.security import hash_password, create_access_token
    from app.models.user import User
    user = User(email="test@test.com", hashed_password=hash_password("pass123"))
    db.add(user)
    await db.flush()
    token = create_access_token(user.id)
    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

## API 테스트 패턴

```python
# tests/api/test_orders.py
async def test_create_order_returns_201(auth_client):
    response = await auth_client.post("/api/v1/orders", json={"item": "book", "qty": 2})
    assert response.status_code == 201
    assert response.json()["item"] == "book"

async def test_get_order_not_found_returns_404(auth_client):
    response = await auth_client.get("/api/v1/orders/99999")
    assert response.status_code == 404

async def test_list_orders_returns_only_own(auth_client, db):
    # 다른 사용자의 주문이 노출되지 않는지
    ...
```

## 서비스 테스트 패턴

```python
# tests/services/test_order_service.py
from app.services.order_service import OrderService
from app.schemas.order import OrderCreate

async def test_create_order_deducts_stock(db, mocker):
    mock_stock = mocker.patch("app.services.order_service.StockService.deduct")
    service = OrderService(db)
    await service.create(user_id=1, data=OrderCreate(item="book", qty=1))
    mock_stock.assert_called_once_with("book", 1)

async def test_create_order_raises_when_out_of_stock(db, mocker):
    from app.exceptions import OutOfStockError
    mocker.patch("app.services.order_service.StockService.deduct", side_effect=OutOfStockError)
    service = OrderService(db)
    with pytest.raises(OutOfStockError):
        await service.create(user_id=1, data=OrderCreate(item="book", qty=100))
```
