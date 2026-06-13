---
description: 코드베이스 분석 후 구현 계획서 작성
argument-hint: <기능 설명>
---

# Dev Plan

**Input**: $ARGUMENTS — 구현할 기능 설명

`planner` 에이전트를 실행하여 구현 계획서를 작성합니다.

---

## 실행 순서

1. `app/` 구조 파악 (`find app -name "*.py" | head -30`)
2. 관련 기존 코드 탐색 (유사 도메인의 router, service, repository 확인)
3. `plans/<feature-name>.md` 계획서 작성
4. 사용자에게 계획서 경로 보고 + 승인 요청

계획서 형식은 `planner` 에이전트 참조.
