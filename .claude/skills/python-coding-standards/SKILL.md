---
name: python-coding-standards
description: Python coding standards — type hints, PEP 8, ruff config, docstring policy, import ordering. Use for Python code quality work.
origin: local
---

# Python Coding Standards

## 타입 힌트

```python
# 모든 함수에 파라미터와 반환 타입 필수
async def get_user(user_id: int, db: AsyncSession) -> User | None:
    ...

# 복잡한 타입은 TypeAlias 사용 (3.10+)
type UserId = int
type UserMap = dict[UserId, User]

# Generic
from typing import TypeVar, Generic
T = TypeVar("T")

class Repository(Generic[T]):
    async def get_by_id(self, id: int) -> T | None: ...
```

## ruff 설정 (pyproject.toml)

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "B", "I", "N", "UP", "S", "ANN"]
ignore = ["ANN101", "ANN102"]  # self, cls 타입힌트 생략 허용

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]  # assert 허용
"alembic/**" = ["ANN"]  # 마이그레이션 타입힌트 생략 허용
```

## mypy 설정

```toml
[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true
exclude = ["alembic/"]
```

## 파일 구조 컨벤션

```python
# 파일 첫 줄: 한국어 역할 주석
# 사용자 계정 관련 비즈니스 로직을 처리하는 서비스

# 임포트 (isort 순서)
from __future__ import annotations  # 필요 시 (순환 임포트 해결)

import asyncio  # 표준 라이브러리
from datetime import datetime

from fastapi import Depends  # 서드파티
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings  # 로컬
from app.models.user import User
```

## 클래스 컨벤션

```python
class UserService:
    """사용자 도메인 서비스."""  # 한 줄 docstring만 허용

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._repo = UserRepository(db)  # private은 _prefix

    async def get_active_users(self) -> list[User]:
        return await self._repo.list_active()
```

## 예외 계층

```python
class AppException(Exception):
    status_code: int = 400

class NotFoundError(AppException):
    status_code = 404

class ForbiddenError(AppException):
    status_code = 403
```

## 금지 패턴

```python
# 금지: Any 남발
def process(data: Any) -> Any: ...  # ✗
def process(data: dict[str, str]) -> str: ...  # ✓

# 금지: mutable default
def foo(items: list = []) -> None: ...  # ✗
def foo(items: list | None = None) -> None:  # ✓
    items = items or []

# 금지: 로깅 f-string
logger.info(f"user {user_id} created")  # ✗
logger.info("user %s created", user_id)  # ✓
```
