---
description: 린트·타입 에러 자동 수정
argument-hint: (없음)
---

# Dev Fix

린트·타입 오류를 자동으로 수정합니다.

---

## 실행 순서

1. `ruff check . --fix` — 자동 수정 가능한 린트 오류 수정
2. `ruff format .` — 코드 포맷 정렬
3. `ruff check .` — 잔여 오류 확인
4. 잔여 오류가 있으면 `python-build-resolver` 에이전트로 수동 수정
5. `mypy app --ignore-missing-imports` — 타입 오류 확인
6. 타입 오류 수정
7. `pytest -x -q` — 테스트 통과 확인
