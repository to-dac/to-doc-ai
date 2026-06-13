---
paths:
  - "**/*.py"
---
# Hooks 동작 안내

## PostToolUse — Edit/Write 후

Python 파일 수정 시 `ruff check <file>` 자동 실행.

- 린트 통과: `[Hook] 린트 OK`
- 린트 실패: `[Hook] 린트 실패 — /dev fix 실행을 권장합니다`

## Stop — 세션 종료 전

`pyproject.toml` 또는 `requirements.txt`가 있는 프로젝트에서 `ruff check .` 실행.

## 수동 전체 검증

```bash
ruff check . && mypy app && pytest -x -q
```
