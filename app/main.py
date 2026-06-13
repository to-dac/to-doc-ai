import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.core.logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    # 인허가 멀티턴 에이전트를 1회만 컴파일해 보관한다.
    # InMemorySaver 가 thread_id 별 대화를 유지하려면 동일 인스턴스를 재사용해야 한다.
    try:
        from app.agents.permit_agent import build_permit_agent

        app.state.permit_agent = build_permit_agent()
        logger.info("인허가 에이전트 초기화 완료")
    except Exception:
        # 에이전트 초기화 실패(예: 환경변수 미설정)가 앱 기동을 막지 않게 한다.
        # 엔드포인트에서 503 으로 안내한다.
        app.state.permit_agent = None
        logger.exception("인허가 에이전트 초기화 실패 — /permit/chat 은 503 을 반환합니다")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
