---
description: 커버리지 분석 및 미달 영역 테스트 생성
argument-hint: (없음)
---

# Dev Coverage

커버리지를 분석하고 미달 영역에 테스트를 추가합니다.

---

## 실행 순서

1. 커버리지 리포트 생성:

```bash
pytest --cov=app --cov-report=term-missing --cov-report=html -q
```

2. 미달 파일 목록 확인 (80% 미만)
3. 미커버 라인 분석
4. `tdd-guide` 에이전트로 해당 파일의 테스트 추가
5. 커버리지 재확인

## 커버리지 목표

| 레이어 | 목표 |
|--------|------|
| services/ | 90%+ |
| api/ | 80%+ |
| repositories/ | 70%+ |
| core/ | 60%+ |
