"""
openmcp - A collection of optimized MCP services for AI Agents

This package provides a server that offers various MCP (Model Context Protocol) 
services that AI agents can connect to remotely using API keys.

Simple Usage:
    import openmcp
    
    # Super simple interface
    mcp = openmcp.MCP("browseruse")
    session = await mcp.create_session()
    await session.navigate("https://example.com")
    await session.screenshot("page.png")
    
    # Or even simpler with context manager
    async with openmcp.browser() as browser:
        await browser.navigate("https://example.com")
        await browser.click("#button")
        await browser.screenshot("result.png")
    
    # One-liner screenshot
    await openmcp.screenshot("https://example.com", "example.png")
"""

__version__ = "0.1.0"
__author__ = "openmcp contributors"
__email__ = "contact@openmcp.org"

# Server components
from .core.server import OpenMCPServer
from .core.config import Config

# Simple client interface
from .client import MCP, browser, screenshot, test_form, ensure_server_running, MCPError

__all__ = [
    # Server components
    "OpenMCPServer", 
    "Config",
    
    # Simple client interface
    "MCP",
    "browser", 
    "screenshot", 
    "test_form",
    "ensure_server_running",
    "MCPError"
]
