---
description: Alembic 마이그레이션 실행·상태 확인·롤백
argument-hint: [info | migrate | rollback | new <message> | blank for status]
---

# DB Migrate (Alembic)

**Action**: $ARGUMENTS (기본값: `info`)

---

## Phase 1 — DETECT

Alembic 설정 확인:

```bash
[ -f "alembic.ini" ] && echo "Alembic 설정 있음" || echo "alembic.ini 없음"
ls alembic/versions/ 2>/dev/null | head -10
```

`alembic.ini`가 없으면 종료: "alembic.ini를 찾을 수 없습니다. `alembic init alembic`으로 초기화하세요."

---

## Phase 2 — INFO (현재 상태)

`$ARGUMENTS`가 비어 있거나 `info`인 경우:

```bash
alembic current         # 현재 적용된 리비전
alembic history --verbose  # 전체 마이그레이션 이력
```

현재 리비전, 적용 여부, 대기 중인 마이그레이션 보고.

---

## Phase 3 — MIGRATE (최신 적용)

`$ARGUMENTS`가 `migrate`인 경우:

```bash
# 대기 중인 마이그레이션 확인
alembic heads
alembic current

# 실행
alembic upgrade head
```

실행 후 `alembic current`로 검증.

---

## Phase 4 — NEW (새 마이그레이션 생성)

`$ARGUMENTS`가 `new <message>`인 경우:

```bash
# 모델 변경사항에서 자동 생성
alembic revision --autogenerate -m "<message>"
```

> **주의**: 자동 생성 파일은 반드시 수동 검토. 특히 아래 항목 확인.
> - `NOT NULL` 컬럼 추가 시 `server_default` 지정 여부
> - `downgrade()` 함수 구현 여부 (`pass`는 롤백 불가)
> - 인덱스 자동 감지 누락 여부

---

## Phase 5 — ROLLBACK

`$ARGUMENTS`가 `rollback`인 경우:

```bash
# 1단계 롤백
alembic downgrade -1

# 특정 리비전으로 롤백
alembic downgrade <revision_id>

# 초기 상태로 (주의!)
# alembic downgrade base
```

롤백 후 `alembic current`로 상태 확인.

---

## Output

```
DB Migration (Alembic) — <날짜>
Action: info | migrate | new | rollback

Current revision: <hash>
Pending: N개

Status: SUCCESS | FAILED | NO_CHANGES
```

> 마이그레이션 파일 작성 시 `skill: database-migrations` 참조.
