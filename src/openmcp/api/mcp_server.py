"""
Official MCP Server implementation using FastMCP

This provides proper MCP protocol support with SSE and streamable-http transports.
"""

import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from mcp.server.fastmcp import FastMCP

from ..core.config import Config
from ..core.mcp_registry import MCPRegistry
from ..services import BrowseruseService, WebSearchService, WebCrawlerService


def create_mcp_app(config_path: Optional[Path] = None) -> FastMCP:
    """Create a FastMCP app with OpenMCP tools"""
    
    # Initialize config and registry
    config = Config.from_file(config_path)
    mcp_registry = MCPRegistry()
    
    # Register services
    mcp_registry.register_service_class("browseruse", BrowseruseService)
    mcp_registry.register_service_class("web_search", WebSearchService)  
    mcp_registry.register_service_class("web_crawler", WebCrawlerService)
    
    # Create FastMCP app
    app = FastMCP()
    
    # Start services synchronously for tool registration
    async def start_services():
        for service_config in config.services:
            if service_config.enabled:
                await mcp_registry.start_service(service_config.name, service_config.config)
    
    # Run startup in event loop if available, otherwise create one
    try:
        loop = asyncio.get_running_loop()
        # If we're in an async context, schedule the startup
        asyncio.create_task(start_services())
    except RuntimeError:
        # No event loop running, create one temporarily
        asyncio.run(start_services())
    
    # Register all tools from services
    for service_name in mcp_registry.list_services():
        service = mcp_registry.get_service(service_name)
        if service:
            service_tools = service.get_tools()
            
            for tool_info in service_tools:
                tool_name = tool_info["name"] 
                tool_description = tool_info.get("description", "")
                
                # Create the tool function dynamically
                def create_tool_func(svc, tname):
                    async def tool_func(**kwargs) -> str:
                        try:
                            result = await svc.call_tool(tname, kwargs)
                            
                            if isinstance(result, dict):
                                if "error" in result:
                                    return f"Error: {result['error']}"
                                else:
                                    import json
                                    return json.dumps(result, indent=2)
                            else:
                                return str(result)
                                
                        except Exception as e:
                            return f"Error executing {tname}: {str(e)}"
                    
                    return tool_func
                
                # Register the tool
                tool_func = create_tool_func(service, tool_name)
                tool_func.__name__ = tool_name
                app.tool(description=tool_description)(tool_func)
    
    return app


def run_sse_server(config_path: Optional[Path] = None, host: str = "0.0.0.0", port: int = 9001):
    """Run FastMCP server with SSE transport"""
    print(f"🚀 Starting OpenMCP FastMCP Server (SSE) on {host}:{port}")
    print("⚠️  Note: FastMCP SSE transport uses default port configuration")
    app = create_mcp_app(config_path)
    app.run(transport="sse")


def run_streamable_http_server(config_path: Optional[Path] = None, host: str = "0.0.0.0", port: int = 9002):
    """Run FastMCP server with streamable-http transport"""
    print(f"🚀 Starting OpenMCP FastMCP Server (streamable-http) on {host}:{port}")
    print("⚠️  Note: FastMCP streamable-http transport uses default port configuration")
    app = create_mcp_app(config_path)
    app.run(transport="streamable-http")