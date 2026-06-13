---
description: 기능 개발 전체 워크플로우 — 계획 → 구현 → 테스트 순서로 실행
argument-hint: <기능 설명>
---

# Dev

**Input**: $ARGUMENTS — 구현할 기능 설명

`/dev plan` → `/dev run` → `/dev test` 를 순서대로 실행합니다.

---

## Step 1 — PLAN

`/dev plan $ARGUMENTS` 실행.

구현 계획서가 완성되면 사용자에게 확인을 받는다.
계획이 승인되면 Step 2로 진행한다.

## Step 2 — RUN

`/dev run <계획서 경로>` 실행.

구현이 완료되고 `ruff check . && mypy app`이 통과되면 Step 3으로 진행한다.

## Step 3 — TEST

`/dev test` 실행.

테스트가 통과되고 커버리지 80%+ 확인되면 완료를 보고한다.

---

## 완료 리포트

```
Dev — <기능명>
─────────────────────────
Plan    DONE  <계획서 경로>
Run     DONE  <변경 파일 수>개 파일
Test    DONE  <테스트 수>개 통과 / 커버리지 XX%
─────────────────────────
Next: /git commit → /git pr
```
