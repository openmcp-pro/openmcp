#!/usr/bin/env python3
"""
Simple SSE Demo with MCP Client

Shows how to use the MCP client library with OpenMCP's SSE streaming.
Combines MCP client patterns with real-time progress updates.
"""

import asyncio
import json
import base64
import httpx
from typing import Dict, Any
from contextlib import asynccontextmanager

# MCP library imports for proper client structure
from mcp.types import Tool, TextContent


class SimpleMCPClient:
    """Simple MCP client for OpenMCP with SSE support"""
    
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url.rstrip("/")
        self.client = None
    
    @asynccontextmanager
    async def connect(self):
        """Connect to OpenMCP server using MCP pattern"""
        self.client = httpx.AsyncClient()
        try:
            print("✅ Connected to OpenMCP via MCP client")
            yield self
        finally:
            if self.client:
                await self.client.aclose()
    
    async def call_tool_stream(self, name: str, arguments: Dict[str, Any] = None, session_id: str = None):
        """Call a tool with streaming progress (MCP + SSE)"""
        if not self.client:
            raise Exception("Not connected")
        
        request_data = {
            "tool_name": name,
            "arguments": arguments or {}
        }
        if session_id:
            request_data["session_id"] = session_id
        
        async with self.client.stream(
            "POST",
            f"{self.base_url}/api/v1/services/browseruse/stream",
            json=request_data
        ) as response:
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        yield json.loads(line[6:])
                    except json.JSONDecodeError:
                        continue


async def simple_sse_demo():
    """Simple demonstration of SSE streaming with MCP client"""
    print("📡 Simple SSE Demo with MCP Client")
    print("=" * 45)
    print("🎭 Using MCP client pattern with SSE streaming")
    print("🏠 No authentication needed from localhost!")
    print()
    
    mcp = SimpleMCPClient()
    
    async with mcp.connect():
        session_id = None
        
        # Create session with streaming progress
        print("🚀 Creating browser session...")
        async for event in mcp.call_tool_stream("create_session", {"headless": True}):
            if event.get("type") == "progress":
                progress = event.get("progress", 0)
                message = event.get("message", "")
                bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
                print(f"   📊 {message} [{bar}] {progress}%")
            elif event.get("type") == "success":
                session_id = event["result"]["session_id"]
                print(f"   ✅ Session created: {session_id[:8]}...")
                break
        
        if not session_id:
            print("❌ Failed to create session")
            return
        
        # Navigate with streaming progress
        print("\n🌐 Navigating to example.com...")
        async for event in mcp.call_tool_stream("navigate", {"url": "https://example.com"}, session_id):
            if event.get("type") == "progress":
                progress = event.get("progress", 0)
                message = event.get("message", "")
                bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
                print(f"   📊 {message} [{bar}] {progress}%")
            elif event.get("type") == "success":
                result = event.get("result", {})
                print(f"   ✅ Navigated to: {result.get('title', 'Unknown')}")
                break
        
        # Screenshot with streaming progress
        print("\n📸 Taking screenshot...")
        screenshot_data = None
        async for event in mcp.call_tool_stream("take_screenshot", {}, session_id):
            if event.get("type") == "progress":
                progress = event.get("progress", 0)
                message = event.get("message", "")
                bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
                print(f"   📊 {message} [{bar}] {progress}%")
            elif event.get("type") == "success":
                screenshot_data = event["result"].get("screenshot")
                print(f"   ✅ Screenshot captured")
                break
        
        # Save screenshot
        if screenshot_data:
            try:
                screenshot_bytes = base64.b64decode(screenshot_data)
                filename = "simple_mcp_sse_demo.png"
                with open(filename, "wb") as f:
                    f.write(screenshot_bytes)
                print(f"   💾 Screenshot saved: {filename}")
            except Exception as e:
                print(f"   ⚠️  Could not save screenshot: {e}")
        
        # Close session with streaming
        print("\n🧹 Closing session...")
        async for event in mcp.call_tool_stream("close_session", {}, session_id):
            if event.get("type") == "success":
                print("   ✅ Session closed successfully")
                break
        
        print("\n🎉 MCP SSE demo completed!")
        print("📋 Benefits:")
        print("   • Clean MCP client interface")
        print("   • Real-time progress via SSE")
        print("   • Official MCP library integration")
        print("   • No API key needed (localhost)")


if __name__ == "__main__":
    asyncio.run(simple_sse_demo())