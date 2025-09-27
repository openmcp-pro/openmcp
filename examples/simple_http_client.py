#!/usr/bin/env python3
"""
Simple HTTP Client Example (Working Alternative)

Since the MCP stdio approach has some complexity with subprocess management,
this example shows the working HTTP API approach that users can rely on.
"""

import asyncio
import json
import base64
import httpx


async def simple_http_demo():
    """Simple demonstration using HTTP API (localhost auth bypass)"""
    print("📡 Simple HTTP Client Demo")
    print("=" * 40)
    print("🌐 Using direct HTTP calls to OpenMCP API")
    print("🏠 Using localhost auth bypass (no API key needed)")
    print()
    
    try:
        async with httpx.AsyncClient() as client:
            print("✅ Connected to OpenMCP via HTTP API")
            
            # Create a browser session
            print("\n🚀 Creating browser session...")
            create_response = await client.post(
                "http://localhost:9000/api/v1/services/browseruse/call",
                json={
                    "tool_name": "create_session",
                    "arguments": {"headless": True, "timeout": 30}
                }
            )
            
            if create_response.status_code != 200:
                print(f"❌ HTTP Error: {create_response.status_code}")
                print(f"Response: {create_response.text}")
                return
            
            result = create_response.json()
            if not result.get("success"):
                print(f"❌ Error: {result.get('error')}")
                return
            
            session_id = result["result"]["session_id"]
            print(f"✅ Browser session created: {session_id}")
            
            # Navigate to a website
            print("\n🌐 Navigating to example.com...")
            nav_response = await client.post(
                "http://localhost:9000/api/v1/services/browseruse/call",
                json={
                    "tool_name": "navigate",
                    "arguments": {"url": "https://example.com"},
                    "session_id": session_id
                }
            )
            
            if nav_response.status_code == 200:
                nav_result = nav_response.json()
                if nav_result.get("success"):
                    title = nav_result["result"].get("title", "Unknown page")
                    print(f"✅ Navigated to: {title}")
                else:
                    print(f"❌ Navigation failed: {nav_result.get('error')}")
            else:
                print(f"❌ Navigation HTTP error: {nav_response.status_code}")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            screenshot_response = await client.post(
                "http://localhost:9000/api/v1/services/browseruse/call",
                json={
                    "tool_name": "take_screenshot",
                    "arguments": {},
                    "session_id": session_id
                }
            )
            
            if screenshot_response.status_code == 200:
                screenshot_result = screenshot_response.json()
                if screenshot_result.get("success"):
                    # Save screenshot
                    screenshot_b64 = screenshot_result["result"]["screenshot"]
                    screenshot_bytes = base64.b64decode(screenshot_b64)
                    filename = "simple_http_demo.png"
                    with open(filename, "wb") as f:
                        f.write(screenshot_bytes)
                    print(f"✅ Screenshot saved: {filename}")
                else:
                    print(f"❌ Screenshot failed: {screenshot_result.get('error')}")
            else:
                print(f"❌ Screenshot HTTP error: {screenshot_response.status_code}")
            
            # Close session
            print("\n🧹 Closing browser session...")
            close_response = await client.post(
                "http://localhost:9000/api/v1/services/browseruse/call",
                json={
                    "tool_name": "close_session",
                    "arguments": {},
                    "session_id": session_id
                }
            )
            
            if close_response.status_code == 200:
                close_result = close_response.json()
                if close_result.get("success"):
                    print("✅ Browser session closed")
                else:
                    print(f"⚠️  Close warning: {close_result.get('error')}")
            
            print("\n🎉 HTTP demo completed successfully!")
            print("📋 Summary:")
            print("   • Connected to OpenMCP via HTTP API")
            print("   • Used localhost auth bypass (no API key needed)")
            print("   • Created browser session")
            print("   • Navigated to website")
            print("   • Captured screenshot")
            print("   • Cleaned up resources")
            
    except Exception as e:
        print(f"❌ HTTP demo failed: {e}")
        print("💡 Make sure OpenMCP HTTP server is running: openmcp serve")


if __name__ == "__main__":
    asyncio.run(simple_http_demo())