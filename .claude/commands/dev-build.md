---
description: 린트·타입 오류 진단 및 수정
argument-hint: (없음)
---

# Dev Build

`python-build-resolver` 에이전트를 실행하여 린트·타입 오류를 진단하고 수정합니다.

---

## 실행 순서

1. `ruff check . 2>&1 | head -50` — 린트 오류 확인
2. `mypy app --ignore-missing-imports 2>&1 | head -50` — 타입 오류 확인
3. `python -c "import app" 2>&1` — 임포트 오류 확인
4. 오류 원인 분석 및 수정
5. 재실행으로 통과 확인

## 자동 수정 가능한 오류

```bash
ruff check . --fix    # 자동 수정 가능한 린트 오류
ruff format .         # 코드 포맷팅
```
