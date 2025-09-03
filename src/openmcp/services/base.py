"""Base class for MCP services."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

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
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call a tool with given arguments."""
        pass
    
    def health_check(self) -> str:
        """Check service health."""
        return "healthy" if self.is_running else "stopped"
    
    def get_info(self) -> Dict[str, Any]:
        """Get service information."""
        return {
            "name": self.__class__.__name__,
            "running": self.is_running,
            "config": self.config,
            "tools": [tool["name"] for tool in self.get_tools()]
        }
