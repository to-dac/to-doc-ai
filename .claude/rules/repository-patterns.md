---
paths:
  - "**/repositories/**/*.py"
---
# Repository 패턴

## 기본 구조

```python
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.foo import Foo
from app.schemas.foo import FooCreate

class FooRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, foo_id: int) -> Foo | None:
        result = await self.db.execute(select(Foo).where(Foo.id == foo_id))
        return result.scalar_one_or_none()

    async def create(self, data: FooCreate) -> Foo:
        foo = Foo(**data.model_dump())
        self.db.add(foo)
        await self.db.flush()
        await self.db.refresh(foo)
        return foo

    async def list_by_owner(self, owner_id: int, offset: int, limit: int) -> list[Foo]:
        result = await self.db.execute(
            select(Foo)
            .where(Foo.owner_id == owner_id)
            .offset(offset)
            .limit(limit)
            .order_by(Foo.created_at.desc())
        )
        return list(result.scalars())
```

## SQLAlchemy 2.x 규칙

- `session.query()` 사용 금지 — `select()` 스타일 필수
- `scalar_one_or_none()` / `scalars().all()` 패턴 사용
- 단일 조회 실패 시 `scalar_one_or_none()` 후 None 반환 — 서비스에서 예외 처리

## Eager Loading

```python
from sqlalchemy.orm import selectinload, joinedload

async def get_with_items(self, order_id: int) -> Order | None:
    result = await self.db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id)
    )
    return result.scalar_one_or_none()
```

## 벌크 연산

```python
async def bulk_update_status(self, ids: list[int], status: str) -> None:
    await self.db.execute(
        update(Foo).where(Foo.id.in_(ids)).values(status=status)
    )
```

## 금지 사항

- Repository에서 비즈니스 로직 수행
- `commit()` 직접 호출 — 커밋은 서비스 레이어 또는 트랜잭션 컨텍스트에서
- lazy load 관계를 루프에서 직접 접근
