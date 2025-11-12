"""Base class for MCP services."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class BaseMCPService(ABC):
    """Base class for all MCP services."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
        self.logger = logger.bind(service=self.__class__.__name__)

    @abstractmethod
    async def start(self) -> None:
        """Start the service."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the service."""
        pass

    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools for this service."""
        pass

    @abstractmethod
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Call a tool with given arguments."""
        pass

    async def call_tool_stream(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        session_id: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream tool execution with real-time updates.

        Override this method in services that support streaming.
        Default implementation provides basic progress updates.
        """
        # Send start event
        yield {
            "type": "start",
            "tool_name": tool_name,
            "session_id": session_id,
            "message": f"Starting {tool_name}",
            "timestamp": asyncio.get_event_loop().time(),
        }

        # Send progress event
        yield {
            "type": "progress",
            "progress": 50,
            "message": "Executing tool...",
            "timestamp": asyncio.get_event_loop().time(),
        }

        try:
            # Execute the tool
            result = await self.call_tool(tool_name, arguments, session_id)

            # Send success event
            yield {
                "type": "success",
                "result": result,
                "session_id": result.get("session_id", session_id),
                "message": "Tool execution completed successfully",
                "timestamp": asyncio.get_event_loop().time(),
            }

        except Exception as e:
            # Send error event
            yield {
                "type": "error",
                "error": str(e),
                "session_id": session_id,
                "message": f"Tool execution failed: {str(e)}",
                "timestamp": asyncio.get_event_loop().time(),
            }

    def supports_streaming(self) -> bool:
        """Check if this service supports streaming."""
        # Check if the service has overridden the call_tool_stream method
        return (
            hasattr(self, "call_tool_stream")
            and self.__class__.call_tool_stream != BaseMCPService.call_tool_stream
        )

    def health_check(self) -> str:
        """Check service health."""
        return "healthy" if self.is_running else "stopped"

    def get_info(self) -> Dict[str, Any]:
        """Get service information."""
        return {
            "name": self.__class__.__name__,
            "running": self.is_running,
            "config": self.config,
            "tools": [tool["name"] for tool in self.get_tools()],
        }
