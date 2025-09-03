#!/usr/bin/env python3
"""
Example MCP client for openmcp using the official MCP protocol.

This example demonstrates how to connect to the openmcp MCP server
and use the browseruse service for web automation.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class OpenMCPClient:
    """MCP client for openmcp server."""
    
    def __init__(self, server_command: List[str]):
        self.server_command = server_command
        self.session: Optional[ClientSession] = None
        self.current_session_id: Optional[str] = None
    
    async def connect(self):
        """Connect to the MCP server."""
        server_params = StdioServerParameters(
            command=self.server_command[0],
            args=self.server_command[1:] if len(self.server_command) > 1 else []
        )
        
        self.session = await stdio_client(server_params)
        await self.session.initialize()
        print("✅ Connected to openmcp MCP server")
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.session:
            await self.session.close()
            print("✅ Disconnected from openmcp MCP server")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools."""
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        result = await self.session.list_tools()
        return [tool.model_dump() for tool in result.tools]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the server."""
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        result = await self.session.call_tool(name, arguments)
        
        # Parse the result from TextContent
        if result.content and len(result.content) > 0:
            content = result.content[0]
            if hasattr(content, 'text'):
                return json.loads(content.text)
        
        return {"error": "No content returned"}
    
    async def create_browser_session(self, headless: bool = True, timeout: int = 30) -> str:
        """Create a new browser session."""
        result = await self.call_tool("create_browser_session", {
            "headless": headless,
            "timeout": timeout
        })
        
        if result.get("success") and "session_id" in result.get("result", {}):
            self.current_session_id = result["result"]["session_id"]
            print(f"✅ Created browser session: {self.current_session_id}")
            return self.current_session_id
        else:
            raise RuntimeError(f"Failed to create session: {result}")
    
    async def navigate(self, url: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Navigate to a URL."""
        session_id = session_id or self.current_session_id
        if not session_id:
            raise RuntimeError("No active session. Create a session first.")
        
        result = await self.call_tool("navigate", {
            "url": url,
            "session_id": session_id
        })
        
        if result.get("success"):
            print(f"✅ Navigated to: {url}")
        else:
            print(f"❌ Navigation failed: {result.get('error')}")
        
        return result
    
    async def find_elements(self, selector: str, by: str = "css", session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find elements on the page."""
        session_id = session_id or self.current_session_id
        if not session_id:
            raise RuntimeError("No active session. Create a session first.")
        
        result = await self.call_tool("find_elements", {
            "selector": selector,
            "by": by,
            "session_id": session_id
        })
        
        if result.get("success"):
            elements = result.get("result", {}).get("elements", [])
            print(f"✅ Found {len(elements)} elements matching '{selector}'")
            return elements
        else:
            print(f"❌ Find elements failed: {result.get('error')}")
            return []
    
    async def click_element(self, selector: str, by: str = "css", session_id: Optional[str] = None) -> Dict[str, Any]:
        """Click an element."""
        session_id = session_id or self.current_session_id
        if not session_id:
            raise RuntimeError("No active session. Create a session first.")
        
        result = await self.call_tool("click_element", {
            "selector": selector,
            "by": by,
            "session_id": session_id
        })
        
        if result.get("success"):
            print(f"✅ Clicked element: {selector}")
        else:
            print(f"❌ Click failed: {result.get('error')}")
        
        return result
    
    async def type_text(self, selector: str, text: str, by: str = "css", session_id: Optional[str] = None) -> Dict[str, Any]:
        """Type text into an element."""
        session_id = session_id or self.current_session_id
        if not session_id:
            raise RuntimeError("No active session. Create a session first.")
        
        result = await self.call_tool("type_text", {
            "selector": selector,
            "text": text,
            "by": by,
            "session_id": session_id
        })
        
        if result.get("success"):
            print(f"✅ Typed text into {selector}: '{text}'")
        else:
            print(f"❌ Type text failed: {result.get('error')}")
        
        return result
    
    async def take_screenshot(self, session_id: Optional[str] = None, save_path: Optional[Path] = None) -> str:
        """Take a screenshot."""
        session_id = session_id or self.current_session_id
        if not session_id:
            raise RuntimeError("No active session. Create a session first.")
        
        result = await self.call_tool("take_screenshot", {
            "session_id": session_id
        })
        
        if result.get("success"):
            screenshot_b64 = result.get("result", {}).get("screenshot", "")
            print("✅ Screenshot taken")
            
            if save_path and screenshot_b64:
                import base64
                screenshot_data = base64.b64decode(screenshot_b64)
                with open(save_path, "wb") as f:
                    f.write(screenshot_data)
                print(f"✅ Screenshot saved to: {save_path}")
            
            return screenshot_b64
        else:
            print(f"❌ Screenshot failed: {result.get('error')}")
            return ""
    
    async def close_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Close a browser session."""
        session_id = session_id or self.current_session_id
        if not session_id:
            return {"success": True, "message": "No session to close"}
        
        result = await self.call_tool("close_session", {
            "session_id": session_id
        })
        
        if result.get("success"):
            print(f"✅ Closed session: {session_id}")
            if session_id == self.current_session_id:
                self.current_session_id = None
        else:
            print(f"❌ Close session failed: {result.get('error')}")
        
        return result


async def example_web_search():
    """Example: Perform a web search using MCP."""
    print("🚀 Starting MCP Web Search Example")
    print("=" * 50)
    
    # Connect to openmcp MCP server
    client = OpenMCPClient(["openmcp", "serve", "--protocol", "mcp"])
    
    try:
        await client.connect()
        
        # List available tools
        print("\n📋 Available Tools:")
        tools = await client.list_tools()
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        # Create browser session
        print("\n🌐 Creating browser session...")
        await client.create_browser_session(headless=True)
        
        # Navigate to DuckDuckGo
        print("\n🔍 Navigating to DuckDuckGo...")
        await client.navigate("https://duckduckgo.com")
        
        # Find search box
        print("\n🔎 Finding search elements...")
        search_elements = await client.find_elements("input[name='q']")
        if search_elements:
            print(f"Found search box: {search_elements[0].get('tag', 'input')}")
        
        # Type search query
        print("\n⌨️  Typing search query...")
        await client.type_text("input[name='q']", "openmcp MCP server")
        
        # Click search button
        print("\n🔍 Clicking search button...")
        await client.click_element("button[type='submit']")
        
        # Wait a moment for results
        await asyncio.sleep(3)
        
        # Take screenshot
        print("\n📸 Taking screenshot...")
        await client.take_screenshot(save_path=Path("mcp_search_results.png"))
        
        # Find search results
        print("\n📊 Finding search results...")
        results = await client.find_elements(".result__title")
        print(f"Found {len(results)} search results")
        
        for i, result in enumerate(results[:3]):
            print(f"  {i+1}. {result.get('text', 'No text')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Clean up
        print("\n🧹 Cleaning up...")
        await client.close_session()
        await client.disconnect()


async def example_form_interaction():
    """Example: Interact with a web form using MCP."""
    print("🚀 Starting MCP Form Interaction Example")
    print("=" * 50)
    
    client = OpenMCPClient(["openmcp", "serve", "--protocol", "mcp"])
    
    try:
        await client.connect()
        
        # Create browser session (non-headless for demo)
        await client.create_browser_session(headless=True)
        
        # Navigate to a form
        print("\n📝 Navigating to test form...")
        await client.navigate("https://httpbin.org/forms/post")
        
        # Fill out form fields
        print("\n✏️  Filling out form...")
        await client.type_text("input[name='custname']", "John Doe")
        await client.type_text("input[name='custtel']", "555-1234")
        await client.type_text("input[name='custemail']", "john@example.com")
        
        # Select radio button
        print("\n🔘 Selecting options...")
        await client.click_element("input[value='medium']")
        
        # Select checkboxes
        await client.click_element("input[value='bacon']")
        await client.click_element("input[value='cheese']")
        
        # Take screenshot
        print("\n📸 Taking screenshot of filled form...")
        await client.take_screenshot(save_path=Path("mcp_form_filled.png"))
        
        print("✅ Form interaction completed!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await client.close_session()
        await client.disconnect()


async def main():
    """Main example function."""
    print("🎯 openmcp MCP Client Examples")
    print("=" * 60)
    
    # Check if openmcp is available
    try:
        result = subprocess.run(["openmcp", "--help"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ openmcp command not found. Please install openmcp first:")
            print("   pip install -e .")
            return
    except FileNotFoundError:
        print("❌ openmcp command not found. Please install openmcp first:")
        print("   pip install -e .")
        return
    
    print("✅ openmcp is available")
    
    # Run examples
    print("\n1️⃣  Web Search Example")
    await example_web_search()
    
    print("\n" + "="*60)
    print("\n2️⃣  Form Interaction Example")
    await example_form_interaction()
    
    print("\n🎉 All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
