---
description: 계획서 기반 코드 구현 및 검증
argument-hint: <계획서 경로>
---

# Dev Run

**Input**: $ARGUMENTS — 계획서 경로 (예: `plans/foo-feature.md`)

계획서를 읽고 단계별로 구현 후 `ruff check . && mypy app`으로 검증합니다.

---

## 실행 순서

1. 계획서 읽기
2. 단계별 구현 (schema → model → repository → service → router 순)
3. 각 파일 첫 줄에 한국어 역할 주석 추가
4. 구현 완료 후:

```bash
ruff check . --fix
mypy app --ignore-missing-imports
```

5. 오류 있으면 수정 후 재실행
6. 통과 시 변경 파일 목록 보고

## Alembic 마이그레이션 필요 시

```bash
alembic revision --autogenerate -m "<변경 내용>"
# 생성된 마이그레이션 파일 반드시 검토
alembic upgrade head
```
