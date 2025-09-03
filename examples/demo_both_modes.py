#!/usr/bin/env python3
"""
Demo script showing both HTTP API and MCP protocol usage.

This script demonstrates the difference between the two approaches
and shows working examples of both.
"""

import asyncio
import json
import subprocess
import time
from pathlib import Path

import httpx


async def demo_http_api():
    """Demonstrate HTTP API usage."""
    print("🌐 HTTP API Demo")
    print("=" * 30)
    
    # Start HTTP server in background
    print("🔧 Starting HTTP server...")
    server_process = subprocess.Popen(
        ["openmcp", "serve", "--host", "127.0.0.1", "--port", "8001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    await asyncio.sleep(3)
    
    try:
        # Get API key from the server's auth manager
        # In a real scenario, you'd get this from the init-config output
        # For demo purposes, we'll create a predictable one
        from openmcp.core.config import Config
        from openmcp.core.auth import AuthManager
        
        config = Config.from_file()
        auth_manager = AuthManager(config.auth)
        api_keys = auth_manager.list_api_keys()
        api_key = list(api_keys.keys())[0]  # Get the first (default) API key
        
        print(f"🔑 Using API key: {api_key[:20]}...")
        
        # Test HTTP API
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Health check
            print("\n📊 Health check...")
            response = await client.get("http://127.0.0.1:8001/health")
            if response.status_code == 200:
                print("✅ Server is healthy")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return
            
            headers = {"Authorization": f"Bearer {api_key}"}
            
            # List services
            print("\n📋 Listing services...")
            response = await client.get(
                "http://127.0.0.1:8001/api/v1/services",
                headers=headers
            )
            
            if response.status_code == 200:
                services = response.json()
                print(f"✅ Found {len(services['running_services'])} running services")
                for service in services['running_services']:
                    print(f"  - {service}")
            else:
                print(f"❌ Failed to list services: {response.status_code}")
                print(response.text)
                return
            
            # Create browser session
            print("\n🌐 Creating browser session...")
            response = await client.post(
                "http://127.0.0.1:8001/api/v1/services/browseruse/call",
                headers=headers,
                json={
                    "tool_name": "create_session",
                    "arguments": {"headless": True, "timeout": 30}
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    session_id = result["result"]["session_id"]
                    print(f"✅ Session created: {session_id}")
                    
                    # Navigate to a website
                    print("\n🔍 Navigating to example.com...")
                    response = await client.post(
                        "http://127.0.0.1:8001/api/v1/services/browseruse/call",
                        headers=headers,
                        json={
                            "tool_name": "navigate",
                            "arguments": {"url": "https://example.com"},
                            "session_id": session_id
                        }
                    )
                    
                    if response.status_code == 200:
                        nav_result = response.json()
                        if nav_result.get("success"):
                            print("✅ Navigation successful")
                            print(f"Page title: {nav_result['result'].get('title', 'Unknown')}")
                        else:
                            print(f"❌ Navigation failed: {nav_result.get('error')}")
                    
                    # Close session
                    print("\n🧹 Closing session...")
                    response = await client.post(
                        "http://127.0.0.1:8001/api/v1/services/browseruse/call",
                        headers=headers,
                        json={
                            "tool_name": "close_session",
                            "arguments": {},
                            "session_id": session_id
                        }
                    )
                    
                    if response.status_code == 200:
                        close_result = response.json()
                        if close_result.get("success"):
                            print("✅ Session closed")
                else:
                    print(f"❌ Session creation failed: {result.get('error')}")
            else:
                print(f"❌ Failed to create session: {response.status_code}")
                print(response.text)
    
    except Exception as e:
        print(f"❌ HTTP API Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Stop server
        print("\n🛑 Stopping HTTP server...")
        server_process.terminate()
        server_process.wait()
        print("✅ HTTP server stopped")


def demo_mcp_concept():
    """Demonstrate MCP concept (without actual implementation)."""
    print("\n🔌 MCP Protocol Concept Demo")
    print("=" * 40)
    
    print("""
🎯 MCP (Model Context Protocol) provides a standardized way for AI agents 
   to interact with external services and tools.

📋 Key Concepts:
   • Tools: Functions that agents can call
   • Resources: Data that agents can read
   • Prompts: Templates for agent interactions
   • Sampling: AI model interactions

🔧 In openmcp, we provide MCP-compatible tools for:
   • Browser automation (navigate, click, type, screenshot)
   • Session management (create, close sessions)
   • Element interaction (find, click, type text)

🌐 Two Access Methods:
   1. HTTP API (what we just demonstrated)
      - Universal access via REST endpoints
      - API key authentication
      - Easy integration with any language
   
   2. Native MCP Protocol (conceptual)
      - Direct MCP protocol compliance
      - JSON-RPC over stdio/websocket
      - Standardized tool discovery
      - Efficient binary communication

📖 Example MCP Tool Definition:
""")
    
    # Show example tool definition
    tool_example = {
        "name": "navigate",
        "description": "Navigate to a URL in the browser",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to navigate to"},
                "session_id": {"type": "string", "description": "Browser session ID"}
            },
            "required": ["url", "session_id"]
        }
    }
    
    print(json.dumps(tool_example, indent=2))
    
    print("""
🚀 Usage Patterns:
   • AI Agent discovers available tools
   • Agent calls tools with structured arguments
   • Server executes tools and returns results
   • Agent uses results to continue task

✅ Benefits of openmcp approach:
   • Provides both HTTP and MCP access
   • Scalable and production-ready
   • Secure with API key authentication
   • Easy to extend with new services
""")


async def main():
    """Main demo function."""
    print("🎯 openmcp Service Demo")
    print("=" * 50)
    
    # Check if openmcp is installed
    try:
        result = subprocess.run(["openmcp", "--help"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ openmcp not found. Please install with: pip install -e .")
            return
    except FileNotFoundError:
        print("❌ openmcp not found. Please install with: pip install -e .")
        return
    
    # Check if config exists
    if not Path("config.yaml").exists():
        print("📝 Creating configuration...")
        subprocess.run(["openmcp", "init-config"], check=True)
    
    print("✅ openmcp is ready")
    
    # Demo HTTP API
    await demo_http_api()
    
    # Demo MCP concept
    demo_mcp_concept()
    
    print("\n🎉 Demo completed!")
    print("\n📚 Next steps:")
    print("   • Try examples/python_client.py for full HTTP client")
    print("   • Try examples/curl_examples.sh for curl examples")
    print("   • Read MCP_EXAMPLES.md for detailed documentation")
    print("   • Extend with your own MCP services!")


if __name__ == "__main__":
    asyncio.run(main())
