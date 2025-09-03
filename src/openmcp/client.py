"""
Super simple MCP client interface for openmcp.

Usage:
    import openmcp
    
    # Simple usage
    mcp = openmcp.MCP("browseruse")
    session = await mcp.create_session()
    await session.navigate("https://example.com")
    await session.screenshot("page.png")
    
    # Or even simpler
    async with openmcp.browser() as browser:
        await browser.navigate("https://example.com")
        await browser.click("#button")
        await browser.screenshot("result.png")
"""

import asyncio
import base64
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

import httpx


class MCPError(Exception):
    """Base exception for MCP operations."""
    pass


class BrowserSession:
    """Represents a browser session with convenient methods."""
    
    def __init__(self, client: 'MCPClient', session_id: str):
        self.client = client
        self.session_id = session_id
        self._closed = False
    
    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL."""
        if self._closed:
            raise MCPError("Session is closed")
        
        result = await self.client._call_tool("navigate", {
            "url": url,
            "session_id": self.session_id
        })
        
        if not result.get("success"):
            raise MCPError(f"Navigation failed: {result.get('error')}")
        
        return result["result"]
    
    async def click(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Click an element."""
        if self._closed:
            raise MCPError("Session is closed")
        
        result = await self.client._call_tool("click_element", {
            "selector": selector,
            "by": by,
            "session_id": self.session_id
        })
        
        if not result.get("success"):
            raise MCPError(f"Click failed: {result.get('error')}")
        
        return result["result"]
    
    async def type(self, selector: str, text: str, by: str = "css") -> Dict[str, Any]:
        """Type text into an element."""
        if self._closed:
            raise MCPError("Session is closed")
        
        result = await self.client._call_tool("type_text", {
            "selector": selector,
            "text": text,
            "by": by,
            "session_id": self.session_id
        })
        
        if not result.get("success"):
            raise MCPError(f"Type failed: {result.get('error')}")
        
        return result["result"]
    
    async def find(self, selector: str, by: str = "css") -> List[Dict[str, Any]]:
        """Find elements on the page."""
        if self._closed:
            raise MCPError("Session is closed")
        
        result = await self.client._call_tool("find_elements", {
            "selector": selector,
            "by": by,
            "session_id": self.session_id
        })
        
        if not result.get("success"):
            raise MCPError(f"Find failed: {result.get('error')}")
        
        return result["result"].get("elements", [])
    
    async def screenshot(self, filename: Optional[str] = None, save_dir: str = "screenshots") -> str:
        """Take a screenshot and save it."""
        if self._closed:
            raise MCPError("Session is closed")
        
        result = await self.client._call_tool("take_screenshot", {
            "session_id": self.session_id
        })
        
        if not result.get("success"):
            raise MCPError(f"Screenshot failed: {result.get('error')}")
        
        # Save screenshot
        screenshot_b64 = result["result"]["screenshot"]
        screenshot_data = base64.b64decode(screenshot_b64)
        
        if not filename:
            from datetime import datetime
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        # Ensure save directory exists
        save_path = Path(save_dir)
        save_path.mkdir(exist_ok=True)
        
        filepath = save_path / filename
        with open(filepath, "wb") as f:
            f.write(screenshot_data)
        
        return str(filepath)
    
    async def page_info(self) -> Dict[str, Any]:
        """Get current page information."""
        if self._closed:
            raise MCPError("Session is closed")
        
        result = await self.client._call_tool("get_page_info", {
            "session_id": self.session_id
        })
        
        if not result.get("success"):
            raise MCPError(f"Get page info failed: {result.get('error')}")
        
        return result["result"]
    
    async def close(self):
        """Close the browser session."""
        if self._closed:
            return
        
        try:
            result = await self.client._call_tool("close_session", {
                "session_id": self.session_id
            })
            
            if not result.get("success"):
                print(f"Warning: Failed to close session: {result.get('error')}")
        finally:
            self._closed = True
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class MCPClient:
    """Simple MCP client for openmcp services."""
    
    def __init__(self, service_name: str, api_key: Optional[str] = None, base_url: str = "http://localhost:9000"):
        self.service_name = service_name
        self.base_url = base_url.rstrip("/")
        
        # Auto-detect API key
        if not api_key:
            api_key = self._auto_detect_api_key()
        
        if not api_key:
            raise MCPError(
                "No API key provided. Either:\n"
                "1. Pass api_key parameter\n"
                "2. Set OPENMCP_API_KEY environment variable\n"
                "3. Run 'openmcp init-config' to create one"
            )
        
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def _auto_detect_api_key(self) -> Optional[str]:
        """Auto-detect API key from various sources."""
        # Try environment variable first
        api_key = os.getenv("OPENMCP_API_KEY")
        if api_key:
            return api_key
        
        # Try to read from config file
        try:
            import yaml
            config_path = Path("config.yaml")
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)
                
                # Try to get API key from running server's auth manager
                from .core.config import Config
                from .core.auth import AuthManager
                
                config_obj = Config.from_file()
                auth_manager = AuthManager(config_obj.auth)
                api_keys = auth_manager.list_api_keys()
                
                if api_keys:
                    return list(api_keys.keys())[0]
        except Exception:
            pass
        
        return None
    
    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP service."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/{self.service_name}/call",
                headers=self.headers,
                json={
                    "tool_name": tool_name,
                    "arguments": arguments
                }
            )
            
            if response.status_code != 200:
                raise MCPError(f"HTTP {response.status_code}: {response.text}")
            
            return response.json()
    
    async def create_session(self, headless: bool = True, timeout: int = 30) -> BrowserSession:
        """Create a new browser session."""
        result = await self._call_tool("create_session", {
            "headless": headless,
            "timeout": timeout
        })
        
        if not result.get("success"):
            raise MCPError(f"Failed to create session: {result.get('error')}")
        
        session_id = result["result"]["session_id"]
        return BrowserSession(self, session_id)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the MCP service is healthy."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/health")
            
            if response.status_code != 200:
                raise MCPError(f"Health check failed: HTTP {response.status_code}")
            
            return response.json()
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools for this service."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/services/{self.service_name}/tools",
                headers=self.headers
            )
            
            if response.status_code != 200:
                raise MCPError(f"Failed to list tools: HTTP {response.status_code}")
            
            result = response.json()
            return result.get("tools", [])


# Convenience functions and context managers
class MCP:
    """Main MCP interface - super simple to use!"""
    
    def __init__(self, service_name: str = "browseruse", api_key: Optional[str] = None, base_url: str = "http://localhost:9000"):
        self.client = MCPClient(service_name, api_key, base_url)
    
    async def create_session(self, headless: bool = True, timeout: int = 30) -> BrowserSession:
        """Create a new browser session."""
        return await self.client.create_session(headless, timeout)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        return await self.client.health_check()
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools."""
        return await self.client.list_tools()
    
    # Convenience methods for quick operations
    async def quick_screenshot(self, url: str, filename: Optional[str] = None) -> str:
        """Quick screenshot of any URL."""
        async with await self.create_session() as session:
            await session.navigate(url)
            await asyncio.sleep(2)  # Wait for page load
            return await session.screenshot(filename)
    
    async def quick_navigate(self, url: str) -> BrowserSession:
        """Quick navigation - returns session for further use."""
        session = await self.create_session()
        await session.navigate(url)
        return session


@asynccontextmanager
async def browser(api_key: Optional[str] = None, base_url: str = "http://localhost:9000", headless: bool = True):
    """
    Super convenient context manager for browser automation.
    
    Usage:
        async with openmcp.browser() as browser:
            await browser.navigate("https://example.com")
            await browser.click("#button")
            await browser.screenshot("result.png")
    """
    mcp = MCP("browseruse", api_key, base_url)
    session = await mcp.create_session(headless=headless)
    try:
        yield session
    finally:
        await session.close()


# Even more convenient functions
async def screenshot(url: str, filename: Optional[str] = None, api_key: Optional[str] = None) -> str:
    """Take a quick screenshot of any URL."""
    mcp = MCP("browseruse", api_key)
    return await mcp.quick_screenshot(url, filename)


async def test_form(url: str, form_data: Dict[str, str], api_key: Optional[str] = None) -> str:
    """Quick form testing."""
    async with browser(api_key) as session:
        await session.navigate(url)
        
        for selector, value in form_data.items():
            await session.type(selector, value)
        
        return await session.screenshot("form_test.png")


# Auto-start server if not running
async def ensure_server_running():
    """Ensure openmcp server is running."""
    try:
        mcp = MCP("browseruse")
        await mcp.health_check()
        return True
    except Exception:
        print("⚠️  openmcp server not running. Start it with: openmcp serve")
        return False
