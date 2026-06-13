---
name: database-migrations
description: Alembic migration patterns — async setup, autogenerate, safe column changes, rollback. Use for DB schema changes.
origin: local
---

# Alembic Migration Patterns

## 초기 설정 (async)

```python
# alembic/env.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.models.base import Base

# 모든 모델 임포트 (autogenerate 감지용)
from app.models import user, order, product  # noqa: F401

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    context.configure(url=settings.DATABASE_URL, target_metadata=target_metadata, ...)
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as conn:
        await conn.run_sync(do_run_migrations)
    await engine.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())
```

## 안전한 컬럼 추가

```python
# 위험 — 기존 데이터 있으면 실패
def upgrade() -> None:
    op.add_column("users", sa.Column("status", sa.String(), nullable=False))

# 올바름 — server_default로 기존 데이터 보호
def upgrade() -> None:
    op.add_column("users", sa.Column(
        "status",
        sa.String(20),
        nullable=False,
        server_default="active",
    ))
    # 이후 필요 시 server_default 제거
    op.alter_column("users", "status", server_default=None)
```

## downgrade 반드시 구현

```python
def upgrade() -> None:
    op.create_table("orders", ...)

def downgrade() -> None:
    op.drop_table("orders")  # pass 금지
```

## 인덱스 추가/제거

```python
def upgrade() -> None:
    op.create_index("ix_orders_user_id", "orders", ["user_id"])
    op.create_index("ix_orders_created_at", "orders", ["created_at"])

def downgrade() -> None:
    op.drop_index("ix_orders_created_at", "orders")
    op.drop_index("ix_orders_user_id", "orders")
```

## 데이터 마이그레이션

```python
from sqlalchemy import text

def upgrade() -> None:
    # 스키마 변경
    op.add_column("users", sa.Column("full_name", sa.String()))
    # 데이터 이관
    op.execute(text("UPDATE users SET full_name = first_name || ' ' || last_name"))
    # 불필요 컬럼 제거
    op.drop_column("users", "first_name")
    op.drop_column("users", "last_name")
```

## 일반 명령어

```bash
alembic revision --autogenerate -m "add orders table"
alembic upgrade head          # 최신 적용
alembic downgrade -1          # 1단계 롤백
alembic current               # 현재 상태
alembic history --verbose     # 전체 이력
```
