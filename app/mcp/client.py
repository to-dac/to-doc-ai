import logging
from typing import Any, Dict, List

from app.mcp.servers.registry import MCP_SERVERS

logger = logging.getLogger(__name__)


class MCPClientManager:
    """MCP 서버들을 관리하고 툴 목록을 통합 제공하는 매니저."""

    def __init__(self):
        self._servers = MCP_SERVERS

    async def get_tools(self) -> List[Dict[str, Any]]:
        tools = []
        for server in self._servers:
            try:
                server_tools = await server.list_tools()
                tools.extend(server_tools)
            except Exception as e:
                logger.warning(f"Failed to fetch tools from {server.name}: {e}")
        return tools

    async def call_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        for server in self._servers:
            if await server.has_tool(tool_name):
                return await server.call_tool(tool_name, tool_input)
        raise ValueError(f"Tool '{tool_name}' not found in any MCP server")
