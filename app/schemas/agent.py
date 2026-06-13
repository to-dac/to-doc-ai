from typing import Optional

from pydantic import BaseModel


class AgentRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None


class AgentResponse(BaseModel):
    result: str
    session_id: Optional[str] = None
