---
paths:
  - "**/schemas/**/*.py"
---
# Schema 패턴 (Pydantic v2)

## 기본 구조

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class FooCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None

class FooUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None

class FooResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
```

## Pydantic v2 규칙

- `orm_mode = True` 대신 `model_config = {"from_attributes": True}`
- `parse_obj()` 대신 `model_validate()`
- `.dict()` 대신 `.model_dump()`
- `validator` 대신 `field_validator` / `model_validator`

## Field Validator

```python
from pydantic import field_validator
import re

class UserCreate(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("유효하지 않은 이메일")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("비밀번호는 8자 이상")
        return v
```

## 중첩 스키마

```python
class OrderResponse(BaseModel):
    id: int
    status: str
    items: list[OrderItemResponse]

    model_config = {"from_attributes": True}
```

## 금지 사항

- 스키마에 DB 접근 로직 포함
- `Optional[X]` 대신 `X | None` 사용 권장 (Python 3.10+)
- 응답 스키마에 민감 정보(password hash 등) 포함
