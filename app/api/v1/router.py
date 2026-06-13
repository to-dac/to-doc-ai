from fastapi import APIRouter

from app.api.v1.endpoints import agent

router = APIRouter()

router.include_router(agent.router, prefix="/agent", tags=["agent"])
