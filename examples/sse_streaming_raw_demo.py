#!/usr/bin/env python3
"""
SSE Streaming Demo

Shows how to use OpenMCP's Server-Sent Events (SSE) streaming for real-time
progress updates during browser automation tasks.
"""

import asyncio
import json
import base64
import httpx


async def sse_streaming_demo():
    """Demonstration of SSE streaming with OpenMCP"""
    print("📡 SSE Streaming Demo")
    print("=" * 40)
    print("🌊 Using Server-Sent Events for real-time updates")
    print("🏠 Using localhost auth bypass (no API key needed)")
    print()
    
    try:
        async with httpx.AsyncClient() as client:
            
            # Stream session creation
            print("🚀 Streaming browser session creation...")
            session_id = None
            
            async with client.stream(
                "POST",
                "http://localhost:9000/api/v1/services/browseruse/stream",
                json={
                    "tool_name": "create_session",
                    "arguments": {"headless": True, "timeout": 30}
                }
            ) as response:
                
                if response.status_code != 200:
                    print(f"❌ HTTP Error: {response.status_code}")
                    return
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            event = json.loads(line[6:])
                            event_type = event.get("type")
                            message = event.get("message", "")
                            
                            if event_type == "start":
                                print(f"   🟢 {message}")
                            elif event_type == "progress":
                                progress = event.get("progress", 0)
                                print(f"   📊 {message} ({progress}%)")
                            elif event_type == "success":
                                result = event.get("result", {})
                                session_id = result.get("session_id")
                                print(f"   ✅ Session created: {session_id}")
                                break
                            elif event_type == "error":
                                print(f"   ❌ Error: {event.get('error')}")
                                return
                        except json.JSONDecodeError:
                            continue
            
            if not session_id:
                print("❌ Failed to create session")
                return
            
            # Stream navigation
            print("\n🌐 Streaming navigation to example.com...")
            async with client.stream(
                "POST",
                "http://localhost:9000/api/v1/services/browseruse/stream",
                json={
                    "tool_name": "navigate",
                    "arguments": {"url": "https://example.com"},
                    "session_id": session_id
                }
            ) as nav_response:
                
                page_title = None
                async for line in nav_response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            event = json.loads(line[6:])
                            event_type = event.get("type")
                            message = event.get("message", "")
                            
                            if event_type == "start":
                                print(f"   🟢 {message}")
                            elif event_type == "progress":
                                progress = event.get("progress", 0)
                                print(f"   📊 {message} ({progress}%)")
                            elif event_type == "success":
                                result = event.get("result", {})
                                page_title = result.get("title", "Unknown page")
                                print(f"   ✅ Navigated to: {page_title}")
                                break
                            elif event_type == "error":
                                print(f"   ❌ Navigation error: {event.get('error')}")
                                break
                        except json.JSONDecodeError:
                            continue
            
            # Stream screenshot
            print("\n📸 Streaming screenshot capture...")
            async with client.stream(
                "POST",
                "http://localhost:9000/api/v1/services/browseruse/stream",
                json={
                    "tool_name": "take_screenshot",
                    "arguments": {},
                    "session_id": session_id
                }
            ) as screenshot_response:
                
                screenshot_data = None
                async for line in screenshot_response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            event = json.loads(line[6:])
                            event_type = event.get("type")
                            message = event.get("message", "")
                            
                            if event_type == "start":
                                print(f"   🟢 {message}")
                            elif event_type == "progress":
                                progress = event.get("progress", 0)
                                print(f"   📊 {message} ({progress}%)")
                            elif event_type == "success":
                                result = event.get("result", {})
                                screenshot_data = result.get("screenshot")
                                print(f"   ✅ Screenshot captured")
                                break
                            elif event_type == "error":
                                print(f"   ❌ Screenshot error: {event.get('error')}")
                                break
                        except json.JSONDecodeError:
                            continue
                
                # Save screenshot if we got the data
                if screenshot_data:
                    try:
                        screenshot_bytes = base64.b64decode(screenshot_data)
                        filename = "sse_streaming_demo.png"
                        with open(filename, "wb") as f:
                            f.write(screenshot_bytes)
                        print(f"   💾 Screenshot saved: {filename}")
                    except Exception as e:
                        print(f"   ⚠️  Could not save screenshot: {e}")
            
            # Stream session cleanup
            print("\n🧹 Streaming session cleanup...")
            async with client.stream(
                "POST",
                "http://localhost:9000/api/v1/services/browseruse/stream",
                json={
                    "tool_name": "close_session",
                    "arguments": {},
                    "session_id": session_id
                }
            ) as close_response:
                
                async for line in close_response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            event = json.loads(line[6:])
                            event_type = event.get("type")
                            message = event.get("message", "")
                            
                            if event_type == "start":
                                print(f"   🟢 {message}")
                            elif event_type == "success":
                                print(f"   ✅ Session closed successfully")
                                break
                            elif event_type == "error":
                                print(f"   ⚠️  Close warning: {event.get('error')}")
                                break
                        except json.JSONDecodeError:
                            continue
            
            print("\n🎉 SSE streaming demo completed successfully!")
            print("📋 Summary:")
            print("   • Used Server-Sent Events for real-time progress updates")
            print("   • Localhost auth bypass (no API key needed)")
            print("   • Streamed browser session creation with progress")
            print("   • Streamed navigation with status updates")
            print("   • Streamed screenshot capture with progress")
            print("   • Streamed session cleanup")
            print("\n💡 Benefits of SSE streaming:")
            print("   • Real-time progress visibility")
            print("   • Non-blocking operation monitoring")
            print("   • Better user experience for long-running tasks")
            print("   • Detailed status and error reporting")
            
    except Exception as e:
        print(f"❌ SSE streaming demo failed: {e}")
        print("💡 Make sure OpenMCP HTTP server is running: openmcp serve")


if __name__ == "__main__":
    asyncio.run(sse_streaming_demo())