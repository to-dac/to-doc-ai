---
paths:
  - "**/exceptions/**/*.py"
  - "**/main.py"
---
# 에러 핸들링 패턴

## 도메인 예외 정의

```python
# app/exceptions/__init__.py
class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class NotFoundError(AppException):
    def __init__(self, resource: str, id: int | str) -> None:
        super().__init__(f"{resource} {id}를 찾을 수 없습니다.", 404)

class ForbiddenError(AppException):
    def __init__(self) -> None:
        super().__init__("접근 권한이 없습니다.", 403)

class ConflictError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(message, 409)
```

## 글로벌 핸들러 등록 (main.py)

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.exceptions import AppException

app = FastAPI()

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # 스택 트레이스는 로그에만, 응답엔 일반 메시지
    logger.exception("예기치 못한 오류", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "내부 서버 오류가 발생했습니다."},
    )
```

## 서비스에서 예외 사용

```python
async def get_foo(self, foo_id: int) -> Foo:
    foo = await self.repo.get_by_id(foo_id)
    if foo is None:
        raise NotFoundError("Foo", foo_id)
    return foo
```

## 금지 사항

- 라우터에서 `HTTPException` 직접 raise (글로벌 핸들러 우회됨)
- 빈 except 블록
- 응답에 내부 스택 트레이스 노출
