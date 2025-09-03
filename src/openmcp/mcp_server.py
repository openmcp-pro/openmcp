"""Alternative MCP server implementation using official MCP library."""

import asyncio
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .services.browseruse_service import BrowseruseService


class OpenMCPServer:
    """MCP server using official MCP library."""
    
    def __init__(self):
        self.server = Server("openmcp")
        self.browseruse_service: Optional[BrowseruseService] = None
        self.sessions: Dict[str, str] = {}  # session mapping
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register MCP tools."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="create_browser_session",
                    description="Create a new browser session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "headless": {"type": "boolean", "default": True},
                            "timeout": {"type": "integer", "default": 30}
                        }
                    }
                ),
                Tool(
                    name="navigate",
                    description="Navigate to a URL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"},
                            "session_id": {"type": "string"}
                        },
                        "required": ["url", "session_id"]
                    }
                ),
                Tool(
                    name="find_elements",
                    description="Find elements on the page",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "selector": {"type": "string"},
                            "session_id": {"type": "string"},
                            "by": {"type": "string", "default": "css"}
                        },
                        "required": ["selector", "session_id"]
                    }
                ),
                Tool(
                    name="click_element",
                    description="Click an element",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "selector": {"type": "string"},
                            "session_id": {"type": "string"},
                            "by": {"type": "string", "default": "css"}
                        },
                        "required": ["selector", "session_id"]
                    }
                ),
                Tool(
                    name="type_text",
                    description="Type text into an element",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "selector": {"type": "string"},
                            "text": {"type": "string"},
                            "session_id": {"type": "string"},
                            "by": {"type": "string", "default": "css"}
                        },
                        "required": ["selector", "text", "session_id"]
                    }
                ),
                Tool(
                    name="take_screenshot",
                    description="Take a screenshot",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string"}
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="close_session",
                    description="Close a browser session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string"}
                        },
                        "required": ["session_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            # Initialize browseruse service if needed
            if not self.browseruse_service:
                self.browseruse_service = BrowseruseService({
                    "headless": True,
                    "timeout": 30,
                    "max_sessions": 5
                })
                await self.browseruse_service.start()
            
            # Handle different tools
            if name == "create_browser_session":
                result = await self.browseruse_service.call_tool(
                    "create_session",
                    arguments
                )
            else:
                # For other tools, extract session_id
                session_id = arguments.pop("session_id", None)
                result = await self.browseruse_service.call_tool(
                    name,
                    arguments,
                    session_id
                )
            
            # Return result as TextContent
            import json
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
    
    async def run(self, transport: str = "stdio"):
        """Run the MCP server."""
        if transport == "stdio":
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        else:
            raise ValueError(f"Unsupported transport: {transport}")


# Usage example
if __name__ == "__main__":
    server = OpenMCPServer()
    asyncio.run(server.run())
