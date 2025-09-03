#!/usr/bin/env python3
"""
Simple MCP client example for openmcp.

This example shows how to interact with the openmcp server using
subprocess communication (stdio transport) without requiring
the full MCP client library.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional


class SimpleMCPClient:
    """Simple MCP client using subprocess communication."""
    
    def __init__(self, server_command: list):
        self.server_command = server_command
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
    
    async def start_server(self):
        """Start the MCP server process."""
        self.process = subprocess.Popen(
            self.server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # Send initialization request
        await self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "simple-mcp-client",
                "version": "1.0.0"
            }
        })
        
        # Send initialized notification
        await self._send_notification("notifications/initialized")
        
        print("✅ MCP server started and initialized")
    
    async def stop_server(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("✅ MCP server stopped")
    
    async def _send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the server."""
        if not self.process:
            raise RuntimeError("Server not started")
        
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        
        # Send request
        request_line = json.dumps(request) + "\n"
        self.process.stdin.write(request_line)
        self.process.stdin.flush()
        
        # Read response
        response_line = self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from server")
        
        response = json.loads(response_line.strip())
        
        if "error" in response:
            raise RuntimeError(f"Server error: {response['error']}")
        
        return response.get("result", {})
    
    async def _send_notification(self, method: str, params: Dict[str, Any] = None):
        """Send a JSON-RPC notification to the server."""
        if not self.process:
            raise RuntimeError("Server not started")
        
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        
        notification_line = json.dumps(notification) + "\n"
        self.process.stdin.write(notification_line)
        self.process.stdin.flush()
    
    async def list_tools(self) -> list:
        """List available tools."""
        result = await self._send_request("tools/list")
        return result.get("tools", [])
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool."""
        result = await self._send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
        
        # Extract content from the response
        content = result.get("content", [])
        if content and len(content) > 0:
            text_content = content[0].get("text", "{}")
            return json.loads(text_content)
        
        return {"error": "No content returned"}


async def demo_mcp_interaction():
    """Demonstrate MCP interaction with openmcp server."""
    print("🚀 Simple MCP Client Demo")
    print("=" * 40)
    
    # Create client
    client = SimpleMCPClient(["python", "-m", "openmcp.mcp_server"])
    
    try:
        # Start server
        print("\n🔧 Starting MCP server...")
        await client.start_server()
        
        # List tools
        print("\n📋 Listing available tools...")
        tools = await client.list_tools()
        print(f"Available tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
        
        # Create browser session
        print("\n🌐 Creating browser session...")
        session_result = await client.call_tool("create_browser_session", {
            "headless": True,
            "timeout": 30
        })
        
        if session_result.get("success"):
            session_id = session_result["result"]["session_id"]
            print(f"✅ Session created: {session_id}")
            
            # Navigate to a website
            print("\n🔍 Navigating to example.com...")
            nav_result = await client.call_tool("navigate", {
                "url": "https://example.com",
                "session_id": session_id
            })
            
            if nav_result.get("success"):
                print("✅ Navigation successful")
                print(f"Page title: {nav_result['result'].get('title', 'Unknown')}")
                
                # Take screenshot
                print("\n📸 Taking screenshot...")
                screenshot_result = await client.call_tool("take_screenshot", {
                    "session_id": session_id
                })
                
                if screenshot_result.get("success"):
                    print("✅ Screenshot taken")
                    
                    # Save screenshot
                    import base64
                    screenshot_data = base64.b64decode(screenshot_result["result"]["screenshot"])
                    with open("simple_mcp_screenshot.png", "wb") as f:
                        f.write(screenshot_data)
                    print("✅ Screenshot saved as simple_mcp_screenshot.png")
                
                # Close session
                print("\n🧹 Closing session...")
                close_result = await client.call_tool("close_session", {
                    "session_id": session_id
                })
                
                if close_result.get("success"):
                    print("✅ Session closed")
            else:
                print(f"❌ Navigation failed: {nav_result.get('error')}")
        else:
            print(f"❌ Session creation failed: {session_result.get('error')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Stop server
        print("\n🛑 Stopping server...")
        await client.stop_server()


if __name__ == "__main__":
    asyncio.run(demo_mcp_interaction())
