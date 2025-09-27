#!/usr/bin/env python3
"""
MCP Client with SSE Transport

Uses the official MCP library SSE transport to connect to OpenMCP.
This is the proper way to use MCP client with SSE.
"""

import asyncio
import json
import base64
from typing import Dict, Any

# Official MCP library imports
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession


async def mcp_streamable_http_demo():
    """Demo using official MCP streamable HTTP client with OpenMCP"""
    print("🎭 Official MCP Streamable HTTP Client Demo")
    print("=" * 55)
    print("🔗 Using MCP streamablehttp_client (latest)")
    print("🌊 Official MCP library HTTP streaming")
    print("🏠 Localhost auth bypass")
    print()
    
    # Connect using official MCP streamable HTTP client
    # Note: Connects to FastMCP streamable-http transport
    mcp_url = "http://localhost:8001/mcp"  # FastMCP streamable-http endpoint
    
    try:
        # Use official MCP streamable HTTP client
        async with streamablehttp_client(mcp_url) as (read_stream, write_stream, get_session_id):
            session = ClientSession(read_stream, write_stream)
            async with session:
                print("✅ Connected to OpenMCP via MCP streamable HTTP")
                
                # Initialize session
                await session.initialize()
                
                # Discover server capabilities
                tools_result = await session.list_tools()
                tools = tools_result.tools
                print(f"🔧 Available tools: {[tool.name for tool in tools]}")
                
                # Call a tool exposed by the server
                if tools:
                    # Example: create browser session
                    result = await session.call_tool("create_session", {"headless": True})
                    print(f"📋 Tool result: {result}")
                
                print("🎉 MCP streamable HTTP demo completed!")
                
    except Exception as e:
        print(f"❌ MCP streamable HTTP demo failed: {e}")
        print("💡 Note: Start OpenMCP with 'openmcp serve --transport streamable-http'")


async def mcp_sse_demo():
    """Demo using official MCP SSE client with OpenMCP"""
    print("\n🎭 Official MCP SSE Client Demo")
    print("=" * 45)
    print("🔗 Using MCP sse_client")
    print("🌊 Official MCP library SSE integration")
    print("🏠 Localhost auth bypass")
    print()
    
    # Connect using official MCP SSE client
    from mcp.client.sse import sse_client
    
    # Note: Connects to FastMCP SSE transport
    sse_url = "http://localhost:8000/sse"  # FastMCP SSE endpoint
    
    try:
        # Use official MCP SSE client
        async with sse_client(sse_url) as (read_stream, write_stream):
            session = ClientSession(read_stream, write_stream)
            async with session:
                print("✅ Connected to OpenMCP via MCP SSE client")
                
                # Initialize session
                await session.initialize()
                
                # Discover server capabilities
                tools_result = await session.list_tools()
                tools = tools_result.tools
                print(f"🔧 Available tools: {[tool.name for tool in tools]}")
                
                # Call a tool exposed by the server
                if tools:
                    # Example: create browser session
                    result = await session.call_tool("create_session", {"headless": True})
                    print(f"📋 Tool result: {result}")
                
                print("🎉 MCP SSE demo completed!")
                
    except Exception as e:
        print(f"❌ MCP SSE demo failed: {e}")
        print("💡 Note: Start OpenMCP with 'openmcp serve --transport sse'")


async def fallback_demo():
    """Fallback demo showing how it should work"""
    print("\n📝 Expected MCP SSE Usage Pattern")
    print("=" * 45)
    
    print("🔧 Proper MCP SSE client code:")
    print("""
    from mcp.client.sse import SSEClientTransport
    from mcp.client.session import ClientSession
    
    # Connect over SSE
    transport = SSEClientTransport("http://localhost:9000/mcp/sse")
    async with transport:
        session = ClientSession(transport)
        async with session:
            # Discover server capabilities
            tools = await session.list_tools()
            print("Tools:", tools)

            # Call a tool exposed by the server
            result = await session.call_tool("create_session", {"headless": True})
            print("Result:", result)
    """)
    
    print("\n💡 Requirements for OpenMCP:")
    print("   • Implement MCP SSE endpoint at /mcp/sse")
    print("   • Follow MCP protocol specification")
    print("   • Return proper MCP responses")
    print("   • Support tool discovery and execution")
    
    print("\n🔄 Current OpenMCP Integration:")
    print("   • Uses custom HTTP/SSE endpoints")
    print("   • Compatible with MCP client patterns")
    print("   • Provides real-time streaming")
    print("   • Works with localhost auth bypass")


async def working_alternative_demo():
    """Show the working alternative using our current approach"""
    print("\n🌊 Working SSE Demo (Current Approach)")
    print("=" * 50)
    
    # Import our working client
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    try:
        # Use our working SSE client approach
        import httpx
        
        async with httpx.AsyncClient() as client:
            print("✅ Connected using working HTTP/SSE approach")
            
            # Stream session creation
            session_id = None
            async with client.stream(
                "POST",
                "http://localhost:9000/api/v1/services/browseruse/stream",
                json={
                    "tool_name": "create_session",
                    "arguments": {"headless": True}
                }
            ) as response:
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            event = json.loads(line[6:])
                            if event.get("type") == "progress":
                                progress = event.get("progress", 0)
                                message = event.get("message", "")
                                print(f"   📊 {message} ({progress}%)")
                            elif event.get("type") == "success":
                                session_id = event["result"]["session_id"]
                                print(f"   ✅ Session created: {session_id[:8]}...")
                                break
                        except json.JSONDecodeError:
                            continue
            
            if session_id:
                # Close session
                await client.post(
                    "http://localhost:9000/api/v1/services/browseruse/call",
                    json={
                        "tool_name": "close_session",
                        "arguments": {},
                        "session_id": session_id
                    }
                )
                print("   ✅ Session closed")
            
            print("🎉 Working SSE demo completed!")
            
    except Exception as e:
        print(f"❌ Working demo failed: {e}")


async def main():
    """Run all demos"""
    print("📡 MCP Client Transport Demonstration (v1.15.0)")
    print("=" * 65)
    
    # Try official MCP streamable HTTP (latest)
    await mcp_streamable_http_demo()
    
    # Try official MCP SSE 
    await mcp_sse_demo()
    
    # Show expected usage pattern
    await fallback_demo()
    
    # Show working alternative
    await working_alternative_demo()
    
    print(f"\n📋 Summary:")
    print(f"   🎯 Latest: MCP v1.15.0 with streamablehttp_client")
    print(f"   🌊 Alternative: MCP SSE client transport")
    print(f"   🔧 Current: Custom HTTP/SSE with MCP-style patterns")
    print(f"   ✅ Working: Examples demonstrate all approaches")


if __name__ == "__main__":
    asyncio.run(main())