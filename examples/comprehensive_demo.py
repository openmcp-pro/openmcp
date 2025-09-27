#!/usr/bin/env python3
"""
Comprehensive OpenMCP Integration Demo

Shows three different ways to integrate with OpenMCP:
1. Simple HTTP API calls
2. SSE streaming for real-time updates
3. Python client library for convenience

All approaches use localhost authentication bypass.
"""

import asyncio
import json
import base64
import httpx
import sys
import os

# Add the src directory to Python path for client library
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import openmcp


async def demo_http_api():
    """Demo 1: Simple HTTP API approach"""
    print("🌐 Demo 1: HTTP API Approach")
    print("=" * 45)
    print("📦 Direct HTTP calls to OpenMCP API")
    print("🏠 Using localhost auth bypass")
    print()
    
    try:
        async with httpx.AsyncClient() as client:
            # Create session
            response = await client.post(
                "http://localhost:9000/api/v1/services/browseruse/call",
                json={
                    "tool_name": "create_session",
                    "arguments": {"headless": True}
                }
            )
            
            if response.status_code != 200:
                print(f"❌ HTTP Error: {response.status_code}")
                return
            
            result = response.json()
            if not result.get("success"):
                print(f"❌ Error: {result.get('error')}")
                return
            
            session_id = result["result"]["session_id"]
            print(f"✅ Session created: {session_id}")
            
            # Navigate
            nav_response = await client.post(
                "http://localhost:9000/api/v1/services/browseruse/call",
                json={
                    "tool_name": "navigate",
                    "arguments": {"url": "https://httpbin.org/html"},
                    "session_id": session_id
                }
            )
            
            if nav_response.status_code == 200:
                nav_result = nav_response.json()
                if nav_result.get("success"):
                    print(f"✅ Navigated successfully")
            
            # Close session
            await client.post(
                "http://localhost:9000/api/v1/services/browseruse/call",
                json={
                    "tool_name": "close_session",
                    "arguments": {},
                    "session_id": session_id
                }
            )
            print("✅ Session closed")
            
    except Exception as e:
        print(f"❌ HTTP demo failed: {e}")


async def demo_sse_streaming():
    """Demo 2: SSE streaming approach"""
    print("\n📡 Demo 2: SSE Streaming Approach")
    print("=" * 50)
    print("🌊 Server-Sent Events for real-time updates")
    print("🏠 Using localhost auth bypass")
    print()
    
    try:
        async with httpx.AsyncClient() as client:
            # Stream session creation
            print("🚀 Streaming session creation...")
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
                            event_type = event.get("type")
                            
                            if event_type == "progress":
                                progress = event.get("progress", 0)
                                message = event.get("message", "")
                                print(f"   📊 {message} ({progress}%)")
                            elif event_type == "success":
                                result = event.get("result", {})
                                session_id = result.get("session_id")
                                print(f"   ✅ Session ready: {session_id}")
                                break
                        except json.JSONDecodeError:
                            continue
            
            if session_id:
                # Stream navigation
                print("🌐 Streaming navigation...")
                async with client.stream(
                    "POST",
                    "http://localhost:9000/api/v1/services/browseruse/stream",
                    json={
                        "tool_name": "navigate",
                        "arguments": {"url": "https://httpbin.org/html"},
                        "session_id": session_id
                    }
                ) as nav_response:
                    
                    async for line in nav_response.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                event = json.loads(line[6:])
                                event_type = event.get("type")
                                
                                if event_type == "progress":
                                    progress = event.get("progress", 0)
                                    message = event.get("message", "")
                                    print(f"   📊 {message} ({progress}%)")
                                elif event_type == "success":
                                    print(f"   ✅ Navigation completed")
                                    break
                            except json.JSONDecodeError:
                                continue
                
                # Close session
                await client.post(
                    "http://localhost:9000/api/v1/services/browseruse/call",
                    json={
                        "tool_name": "close_session",
                        "arguments": {},
                        "session_id": session_id
                    }
                )
                print("✅ Session closed")
            
    except Exception as e:
        print(f"❌ SSE demo failed: {e}")


async def demo_python_client():
    """Demo 3: Python client library approach"""
    print("\n🐍 Demo 3: Python Client Library Approach")
    print("=" * 55)
    print("📦 Using openmcp Python client library")
    print("🏠 Using localhost auth bypass")
    print()
    
    try:
        # Simple one-liner screenshot
        print("📸 Quick screenshot using client library:")
        screenshot_path = await openmcp.screenshot("https://httpbin.org/html", "demo_screenshot.png")
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        # More detailed browser automation
        print("\n🚀 Advanced browser automation:")
        async with openmcp.browser() as browser:
            await browser.navigate("https://httpbin.org/forms/post")
            print("✅ Navigated to form page")
            
            # Get page info
            try:
                page_info = await browser.page_info()
                print(f"📄 Page title: {page_info.get('title', 'Unknown')}")
            except Exception:
                print("📄 Page info not available")
            
            # Take final screenshot
            final_screenshot = await browser.screenshot("demo_form.png")
            print(f"✅ Final screenshot: {final_screenshot}")
        
        print("✅ Client library demo completed")
        
    except Exception as e:
        print(f"❌ Client library demo failed: {e}")


async def main():
    """Run all integration demos"""
    print("🚀 OpenMCP Comprehensive Integration Demo")
    print("=" * 60)
    print("🔀 Comparing different integration approaches")
    print()
    
    # Run all demos
    await demo_http_api()
    await demo_sse_streaming()
    await demo_python_client()
    
    # Summary
    print(f"\n📊 Integration Approaches Summary")
    print("=" * 50)
    print()
    
    print("🌐 HTTP API Approach:")
    print("   ✅ Pros: Simple, direct, any HTTP client")
    print("   ❌ Cons: No real-time feedback, manual JSON handling")
    print()
    
    print("📡 SSE Streaming Approach:")
    print("   ✅ Pros: Real-time progress, visual feedback")
    print("   ❌ Cons: More complex implementation")
    print()
    
    print("🐍 Python Client Library:")
    print("   ✅ Pros: Super convenient, high-level API")
    print("   ❌ Cons: Python-specific, abstracts HTTP details")
    print()
    
    print("💡 Recommendations:")
    print("   🎯 For production automation: Use Python Client Library")
    print("   ⚡ For quick scripts: Use HTTP API")
    print("   📊 For dashboards/monitoring: Use SSE Streaming")
    print()
    
    print("🎉 All integration demos completed!")
    print("📁 Check for screenshot files: *.png")


if __name__ == "__main__":
    asyncio.run(main())