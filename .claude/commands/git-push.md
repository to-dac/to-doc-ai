# Git Commit & Push

변경사항을 커밋하고 원격 저장소에 푸시합니다.

## 실행 순서

1. `git status`로 변경 파일 확인
2. `git diff --staged` + `git diff`로 변경 내용 파악
3. `git log --oneline -5`로 최근 커밋 스타일 확인
4. 변경사항에 맞는 커밋 메시지 작성 (Semantic Commit)
5. 관련 파일 스테이징 후 커밋
6. 현재 브랜치로 push

## 규칙

- 커밋 메시지는 Semantic Commit 형식 (`feat:`, `fix:`, `refactor:`, `chore:` 등)
- 서명 스킵 (`--no-verify`) 금지 — 훅 실패 시 원인 수정
- `.env`, 시크릿 파일 커밋 금지
- `git add .` 대신 파일명 지정으로 스테이징
- force push 금지
- Co-Authored-By 태그 포함:
  ```
  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  ```

## 완료 기준

`git log --oneline -1`로 커밋 확인 + push 성공 메시지 확인.
