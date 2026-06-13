---
description: 로컬 변경(Python 특화) 또는 PR 종합 리뷰
argument-hint: (없음) 또는 PR 번호
---

# Dev Review

`code-reviewer` 에이전트를 실행합니다.

- **인자 없음**: 로컬 변경사항 (`git diff`) 리뷰
- **PR 번호**: 해당 PR의 전체 변경사항 리뷰

---

## 로컬 리뷰 순서

1. `git diff -- '*.py'` — 변경된 Python 파일 확인
2. `ruff check . && mypy app` — 자동화 검사 실행
3. 변경 파일 코드 리뷰 (code-reviewer 에이전트 체크리스트 기준)
4. CRITICAL/HIGH 이슈 발견 시 즉시 보고

## PR 리뷰 순서 (PR 번호 제공 시)

1. `gh pr diff <번호>` — PR 전체 diff 조회
2. 변경된 파일 목록 파악
3. 각 파일 리뷰
4. 발견사항 요약 보고
