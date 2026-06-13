---
description: 현재 FastAPI 프로젝트를 분석하여 CLAUDE.md와 rules를 프로젝트에 맞게 자동 커스터마이징
argument-hint: (없음)
---

# Dev Init

현재 프로젝트의 설정 파일, 패키지 구조, 코드 스타일을 분석하여 CLAUDE.md와 rules를 실제 프로젝트에 맞게 업데이트한다.

---

## Phase 1 — 프로젝트 설정 분석

다음 파일 중 존재하는 것을 읽는다.

- `pyproject.toml`
- `requirements.txt`
- `requirements-dev.txt`
- `setup.py`

추출할 정보.
- **프로젝트명** (name 필드)
- **Python 버전**
- **FastAPI 버전**
- **사용 중인 의존성** — 아래 목록 기준으로 감지

| 의존성 키워드 | 감지 결과 |
|---|---|
| `sqlalchemy`, `asyncpg` | SQLAlchemy 비동기 DB |
| `alembic` | Alembic 마이그레이션 |
| `redis`, `aioredis` | Redis 사용 |
| `celery`, `arq` | 비동기 태스크 큐 |
| `kafka`, `aiokafka` | Kafka 사용 |
| `pydantic-settings` | 환경변수 설정 |
| `pytest-asyncio` | 비동기 테스트 |
| `httpx` | 비동기 HTTP 클라이언트 |

---

## Phase 2 — 패키지 구조 분석

`app/` 디렉토리를 스캔한다.

```bash
find app -type f -name "*.py" | head -50
```

추출할 정보.
- **앱 루트 경로** (app/ vs src/ 등)
- **실제 레이어 디렉토리명** (api vs routers, services vs service 등)
- **도메인 목록** (endpoints/ 하위 서브디렉토리)
- **API 버전 접두사** (v1, v2 등)

---

## Phase 3 — 코드 스타일 샘플링

각 레이어에서 파일 1개씩 읽어 스타일을 파악한다.

| 레이어 | 읽을 파일 | 파악할 내용 |
|---|---|---|
| Router | `*router*.py` 또는 `endpoints/*.py` 중 1개 | 응답 모델, 의존성 패턴 |
| Model | `models/*.py` 중 1개 | Base 클래스, 컬럼 어노테이션 스타일 |
| Service | `services/*.py` 중 1개 | 클래스 구조, 의존성 주입 방식 |
| Schema | `schemas/*.py` 중 1개 | Pydantic v1 vs v2, 네이밍 컨벤션 |
| Test | `tests/**/*.py` 중 1개 | 픽스처 패턴, asyncio 설정 |

---

## Phase 4 — CLAUDE.md 업데이트

`CLAUDE.md`를 읽고 분석 결과로 아래 항목을 업데이트한다.

1. **프로젝트 개요 섹션** — TODO 주석 제거, 실제 프로젝트명과 도메인 설명으로 교체
2. **실행 명령어 섹션** — 실제 진입점 경로(예: `app.main:app`)로 업데이트
3. **아키텍처 섹션** — 실제 디렉토리 구조로 업데이트
4. **기술 스택 섹션** (없으면 추가) — 감지된 의존성 목록 삽입

---

## Phase 5 — Rules 업데이트

분석 결과를 기반으로 `.claude/rules/` 파일들의 예시 코드를 업데이트한다.

| Rule 파일 | 업데이트 내용 |
|---|---|
| `architecture.md` | 실제 디렉토리 구조 반영 |
| `router-patterns.md` | 실제 응답 모델, prefix 패턴 반영 |
| `schema-patterns.md` | Pydantic v1 vs v2 스타일 반영 |
| `service-patterns.md` | 실제 서비스 클래스 구조 반영 |

---

## Phase 6 — 결과 리포트

```
Dev Init 완료
─────────────────────────────────────
프로젝트    <프로젝트명>
Python      3.11
FastAPI     0.115.x
앱 루트     app/
도메인      users, orders, auth (3개)

감지된 스택
  ✓ FastAPI 0.115
  ✓ SQLAlchemy 2.x (asyncpg)
  ✓ Alembic
  ✓ Pydantic v2
  ✓ pytest-asyncio
  ✗ Kafka (미감지)
  ✗ Redis (미감지)

업데이트된 파일
  ✓ CLAUDE.md
  ✓ .claude/rules/architecture.md
  ✓ .claude/rules/router-patterns.md
  ✓ .claude/rules/schema-patterns.md
  ✓ .claude/rules/service-patterns.md
─────────────────────────────────────
초기화 완료. 이제 /dev plan <기능> 으로 시작하세요.
```
