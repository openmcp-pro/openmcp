"""
Official MCP Server implementation using FastMCP

This provides proper MCP protocol support with SSE and streamable-http transports.
"""

import asyncio
import json
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
                
                # Create a tool function with proper closure to capture service and tool_name
                def create_tool_func(service_instance, tool_name_capture, tool_description_capture):
                    
                    # Define specific tool signatures for common tools
                    if tool_name_capture == "create_session":
                        @app.tool(name=tool_name_capture, description=tool_description_capture)
                        async def create_session_tool(headless: bool = True, timeout: int = 30) -> str:
                            try:
                                result = await service_instance.call_tool("create_session", {"headless": headless, "timeout": timeout})
                                return json.dumps(result, indent=2) if isinstance(result, dict) else str(result)
                            except Exception as e:
                                return f"Error executing create_session: {str(e)}"
                        return create_session_tool
                        
                    elif tool_name_capture == "navigate":
                        @app.tool(name=tool_name_capture, description=tool_description_capture)
                        async def navigate_tool(url: str, session_id: str = None) -> str:
                            try:
                                args = {"url": url}
                                if session_id:
                                    args["session_id"] = session_id
                                result = await service_instance.call_tool("navigate", args)
                                return json.dumps(result, indent=2) if isinstance(result, dict) else str(result)
                            except Exception as e:
                                return f"Error executing navigate: {str(e)}"
                        return navigate_tool
                        
                    elif tool_name_capture == "take_screenshot":
                        @app.tool(name=tool_name_capture, description=tool_description_capture)
                        async def take_screenshot_tool(session_id: str = None) -> str:
                            try:
                                args = {}
                                if session_id:
                                    args["session_id"] = session_id
                                result = await service_instance.call_tool("take_screenshot", args)
                                return json.dumps(result, indent=2) if isinstance(result, dict) else str(result)
                            except Exception as e:
                                return f"Error executing take_screenshot: {str(e)}"
                        return take_screenshot_tool
                        
                    elif tool_name_capture == "web_search":
                        @app.tool(name=tool_name_capture, description=tool_description_capture)
                        async def web_search_tool(query: str) -> str:
                            try:
                                result = await service_instance.call_tool("web_search", {"query": query})
                                return json.dumps(result, indent=2) if isinstance(result, dict) else str(result)
                            except Exception as e:
                                return f"Error executing web_search: {str(e)}"
                        return web_search_tool
                        
                    else:
                        # Generic tool handler for other tools
                        @app.tool(name=tool_name_capture, description=tool_description_capture)
                        async def generic_tool(**kwargs) -> str:
                            try:
                                result = await service_instance.call_tool(tool_name_capture, kwargs)
                                
                                if isinstance(result, dict):
                                    if "error" in result:
                                        return f"Error: {result['error']}"
                                    else:
                                        return json.dumps(result, indent=2)
                                else:
                                    return str(result)
                                    
                            except Exception as e:
                                return f"Error executing {tool_name_capture}: {str(e)}"
                        return generic_tool
                
                # Create and register the tool with proper closure
                create_tool_func(service, tool_name, tool_description)
    
    return app


def run_sse_server(config_path: Optional[Path] = None, host: str = "0.0.0.0", port: int = 8000):
    """Run FastMCP server with SSE transport"""
    print(f"🚀 Starting OpenMCP FastMCP Server (SSE) on {host}:{port}")
    print(f"📡 FastMCP SSE endpoint: http://{host}:{port}/sse")
    app = create_mcp_app(config_path)
    app.run(transport="sse")


def run_streamable_http_server(config_path: Optional[Path] = None, host: str = "0.0.0.0", port: int = 8001):
    """Run FastMCP server with streamable-http transport"""
    print(f"🚀 Starting OpenMCP FastMCP Server (streamable-http) on {host}:{port}")
    print(f"📡 FastMCP streamable-http endpoint: http://{host}:{port}/mcp")
    
    # Create FastMCP app and get the ASGI application
    mcp_app = create_mcp_app(config_path)
    asgi_app = mcp_app.streamable_http_app()
    
    # Run with uvicorn
    import uvicorn
    uvicorn.run(asgi_app, host=host, port=port)