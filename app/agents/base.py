import uuid
from typing import Optional

import anthropic

from app.core.config import settings
from app.mcp.client import MCPClientManager


class AgentRunner:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.mcp_manager = MCPClientManager()

    async def run(self, prompt: str, session_id: Optional[str] = None) -> str:
        if session_id is None:
            session_id = str(uuid.uuid4())

        tools = await self.mcp_manager.get_tools()

        response = await self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            tools=tools,
            messages=[{"role": "user", "content": prompt}],
        )

        return self._extract_text(response)

    def _extract_text(self, response) -> str:
        for block in response.content:
            if hasattr(block, "text"):
                return block.text
        return ""
