from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseMCPServer(ABC):
    name: str = ""

    @abstractmethod
    async def list_tools(self) -> List[Dict[str, Any]]:
        """서버가 제공하는 툴 목록 반환."""

    @abstractmethod
    async def call_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """툴 실행 후 결과 반환."""

    async def has_tool(self, tool_name: str) -> bool:
        tools = await self.list_tools()
        return any(t["name"] == tool_name for t in tools)
