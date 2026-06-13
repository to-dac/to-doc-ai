---
description: GitHub 이슈 생성 — bug_report 또는 feature_request 템플릿으로 이슈를 만든다
argument-hint: [bug | feat] <제목>
---

# Create Issue

GitHub 이슈를 생성합니다.

**입력**: $ARGUMENTS
- `bug <제목>` — 버그 리포트 이슈
- `feat <제목>` — 기능 요청 이슈
- 타입 생략 시 대화로 결정

---

## Step 1 — 타입과 제목 파악

`$ARGUMENTS`에서 첫 단어로 타입(`bug` / `feat`)을 판별하고, 나머지를 제목으로 사용한다.
둘 다 없으면 사용자에게 타입과 제목을 묻는다.

## Step 2 — 내용 작성

현재 컨텍스트(변경된 파일, 오류 메시지, 대화 내용)를 바탕으로 이슈 본문을 작성한다.

**bug** 인 경우:
```
## 버그 설명
<현상 요약>

## 재현 절차
1. 
2. 

## 기대 동작
<기대값>

## 실제 동작
<실제값>

## 로그 / 스택 트레이스
<관련 로그>

## 환경
- Spring Boot 버전:
- Java 버전:
```

**feat** 인 경우:
```
## 목적
<왜 필요한지>

## 도메인 / 레이어
- [ ] Controller / Service / Repository / Domain / 인프라

## 제안하는 해결책
<구현 방향>

## 인수 조건
- [ ] 
- [ ] 
```

## Step 3 — 이슈 생성

```bash
gh issue create \
  --title "<제목>" \
  --body "<본문>" \
  --label "<bug|enhancement>"
```

생성된 이슈 URL을 출력한다.
