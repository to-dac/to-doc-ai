---
name: sqlalchemy-patterns
description: SQLAlchemy 2.x async ORM patterns, model definition, relationships, eager loading, bulk operations. Use for FastAPI database work.
origin: local
---

# SQLAlchemy 2.x Async Patterns

## Model 정의

```python
# app/models/base.py
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from datetime import datetime

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
```

```python
# app/models/user.py
# 사용자 계정 및 인증 정보를 저장하는 ORM 모델
from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    orders: Mapped[list["Order"]] = relationship(
        back_populates="user",
        lazy="raise",  # async에서 lazy select 방지
    )

    __table_args__ = (
        Index("ix_users_email", "email"),
    )
```

## 관계 정의 및 Eager Loading

```python
# 1:N 관계
class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    user: Mapped["User"] = relationship(back_populates="orders", lazy="raise")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", lazy="raise")
```

```python
# Eager loading 쿼리
from sqlalchemy.orm import selectinload, joinedload

# 1:N 관계 (selectinload 권장)
stmt = select(Order).options(selectinload(Order.items)).where(Order.id == order_id)

# N:1 관계 (joinedload 권장)
stmt = select(Order).options(joinedload(Order.user)).where(Order.user_id == user_id)
```

## Repository 기본 패턴

```python
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

class OrderRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, order_id: int) -> Order | None:
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int, offset: int, limit: int) -> list[Order]:
        result = await self.db.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .offset(offset).limit(limit)
        )
        return list(result.scalars())

    async def create(self, data: OrderCreate) -> Order:
        order = Order(**data.model_dump())
        self.db.add(order)
        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def bulk_update_status(self, ids: list[int], status: str) -> None:
        await self.db.execute(
            update(Order).where(Order.id.in_(ids)).values(status=status)
        )
```

## 트랜잭션

```python
# 서비스에서 명시적 트랜잭션
async def create_order_with_payment(self, data: OrderCreate) -> Order:
    async with self.db.begin():
        order = await self.order_repo.create(data)
        await self.payment_repo.charge(data.payment_method, order.total)
    return order
```

## Alembic 설정 (async)

```python
# alembic/env.py
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio

def run_async_migrations():
    connectable = create_async_engine(settings.DATABASE_URL)
    async def do_run():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
    asyncio.run(do_run())
```
