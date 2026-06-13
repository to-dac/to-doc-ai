---
description: 린트·타입체크·테스트·커버리지·보안 전체 검증
argument-hint: (없음)
---

# Dev Verify

프로젝트 전체 품질을 종합 검증합니다.

---

## 실행 순서

### 1. 린트 & 포맷
```bash
ruff check .
ruff format --check .
```

### 2. 타입 체크
```bash
mypy app --ignore-missing-imports
```

### 3. 테스트 + 커버리지
```bash
pytest --cov=app --cov-report=term-missing -q
```

### 4. 보안 스캔
```bash
bandit -r app -ll -q 2>/dev/null || echo "bandit 미설치 — pip install bandit"
```

### 5. 의존성 취약점
```bash
pip-audit 2>/dev/null || echo "pip-audit 미설치 — pip install pip-audit"
```

---

## 결과 리포트

```
Dev Verify
─────────────────────────────────────
린트       PASS / FAIL (N개 오류)
타입체크   PASS / FAIL (N개 오류)
테스트     PASS N개 통과 / FAIL
커버리지   XX% (목표: 80%+)
보안       PASS / WARN (N개 경고)
─────────────────────────────────────
```

FAIL 항목은 `/dev fix` 또는 `python-build-resolver`로 수정.
