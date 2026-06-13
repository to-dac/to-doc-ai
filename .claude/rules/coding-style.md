---
paths:
  - "**/*.py"
---
# Python 코딩 스타일

## 타입 힌트

```python
# 모든 함수에 파라미터 타입과 반환 타입 명시
async def get_user(user_id: int, db: AsyncSession) -> User | None:
    ...

# Python 3.10+ 유니온 문법 사용
def process(value: str | None) -> str:
    return value or ""
```

## 임포트 순서 (ruff isort 기준)

```python
# 1. 표준 라이브러리
from datetime import datetime
from typing import Any

# 2. 서드파티
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# 3. 로컬
from app.core.deps import get_current_user
from app.schemas.foo import FooResponse
```

## 파일 첫 줄: 한국어 역할 주석

```python
# 사용자 인증 관련 비즈니스 로직을 처리하는 서비스
from fastapi import ...
```

## 로깅

```python
import logging
logger = logging.getLogger(__name__)

# 올바름 — lazy 포맷
logger.info("사용자 생성: %s", user_id)

# 금지 — f-string (예외 발생 시에도 포맷팅 실행됨)
logger.info(f"사용자 생성: {user_id}")
```

## 상수

```python
# 모듈 수준 상수는 대문자
MAX_RETRY_COUNT = 3
DEFAULT_PAGE_SIZE = 20
```

## 금지 사항

- 함수에 타입힌트 없음
- `Any` 타입 남발
- `print()` 사용 (로거 사용)
- 클래스 변수에 mutable default (`items: list = []`)
