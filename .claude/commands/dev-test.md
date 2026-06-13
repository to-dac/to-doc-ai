---
description: TDD 워크플로우 — 테스트 먼저 작성 후 구현
argument-hint: (없음 또는 테스트 대상 파일)
---

# Dev Test

`tdd-guide` 에이전트를 실행하여 TDD 워크플로우를 진행합니다.

---

## 실행 순서

1. 구현된 코드 확인 (`git diff --name-only`)
2. 테스트 파일 작성 (RED)
3. `pytest tests/ -x --tb=short` 실패 확인
4. 테스트 통과 최소 구현 (GREEN)
5. `pytest tests/ -x` 통과 확인
6. 커버리지 확인:

```bash
pytest --cov=app --cov-report=term-missing -q
```

목표: 서비스 90%+, 라우터 80%+

## 테스트 실행 명령어

```bash
pytest -x -q                          # 전체 (첫 실패 중단)
pytest tests/api/ -x -q               # API 테스트만
pytest tests/services/ -x -q          # 서비스 테스트만
pytest -k "test_create" -v            # 이름 필터
pytest --cov=app --cov-report=html    # 커버리지 HTML
```
