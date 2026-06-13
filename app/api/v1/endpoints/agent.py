from fastapi import APIRouter, HTTPException

from app.agents.base import AgentRunner
from app.schemas.agent import AgentRequest, AgentResponse

router = APIRouter()


@router.post("/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    try:
        runner = AgentRunner()
        result = await runner.run(request.prompt, request.session_id)
        return AgentResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
