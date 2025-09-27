#!/usr/bin/env python3
"""
Server-Sent Events (SSE) Streaming Examples for OpenMCP

Demonstrates real-time streaming of browser operations and web tools.
No API key needed from localhost!
"""

import asyncio
import json
import httpx
from typing import AsyncGenerator, Dict, Any


class OpenMCPStreaming:
    """SSE streaming client for OpenMCP services"""
    
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        # No auth headers needed from localhost!
        self.headers = {}
    
    async def stream_tool_call(
        self, 
        service_name: str, 
        tool_name: str, 
        arguments: Dict[str, Any],
        session_id: str = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream a tool call with real-time updates"""
        
        payload = {
            "tool_name": tool_name,
            "arguments": arguments
        }
        if session_id:
            payload["session_id"] = session_id
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/v1/services/{service_name}/stream",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status_code != 200:
                    raise Exception(f"SSE request failed: {response.status_code}")
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        try:
                            event = json.loads(data)
                            yield event
                        except json.JSONDecodeError:
                            continue


async def example_1_streaming_browser_session():
    """Example 1: Stream browser session creation"""
    print("🚀 Example 1: Streaming Browser Session Creation")
    print("=" * 60)
    
    streaming = OpenMCPStreaming()
    
    try:
        print("📡 Starting browser session with real-time updates...")
        
        session_id = None
        async for event in streaming.stream_tool_call(
            "browseruse",
            "create_session",
            {"headless": True, "timeout": 30}
        ):
            event_type = event.get("type")
            message = event.get("message", "")
            progress = event.get("progress")
            
            if event_type == "start":
                print(f"🟢 {message}")
            elif event_type == "progress":
                progress_bar = "█" * int(progress / 5) + "░" * (20 - int(progress / 5))
                print(f"📊 {message} [{progress_bar}] {progress}%")
            elif event_type == "success":
                session_id = event.get("result", {}).get("session_id")
                print(f"✅ {message}")
                print(f"📋 Session ID: {session_id}")
            elif event_type == "error":
                print(f"❌ Error: {event.get('error')}")
            elif event_type == "complete":
                print(f"🎯 {message}")
        
        return session_id
        
    except Exception as e:
        print(f"❌ Streaming error: {e}")
        return None


async def example_2_streaming_navigation(session_id: str):
    """Example 2: Stream navigation with real-time updates"""
    print(f"\n🌐 Example 2: Streaming Navigation")
    print("=" * 50)
    
    if not session_id:
        print("❌ No session available for navigation")
        return
    
    streaming = OpenMCPStreaming()
    
    try:
        print("📡 Navigating to example.com with real-time updates...")
        
        async for event in streaming.stream_tool_call(
            "browseruse",
            "navigate",
            {"url": "https://example.com"},
            session_id
        ):
            event_type = event.get("type")
            message = event.get("message", "")
            progress = event.get("progress")
            
            if event_type == "start":
                print(f"🟢 {message}")
            elif event_type == "progress":
                if progress:
                    progress_bar = "█" * int(progress / 5) + "░" * (20 - int(progress / 5))
                    print(f"📊 {message} [{progress_bar}] {progress}%")
                else:
                    print(f"📊 {message}")
            elif event_type == "success":
                result = event.get("result", {})
                print(f"✅ {message}")
                print(f"📄 Page title: {result.get('title', 'Unknown')}")
                print(f"🔗 Final URL: {result.get('url', 'Unknown')}")
            elif event_type == "error":
                print(f"❌ Error: {event.get('error')}")
            elif event_type == "complete":
                print(f"🎯 {message}")
                
    except Exception as e:
        print(f"❌ Navigation streaming error: {e}")


async def example_3_streaming_form_interaction(session_id: str):
    """Example 3: Stream form filling with progress updates"""
    print(f"\n📝 Example 3: Streaming Form Interaction")
    print("=" * 50)
    
    if not session_id:
        print("❌ No session available for form interaction")
        return
    
    streaming = OpenMCPStreaming()
    
    try:
        # First navigate to a form page
        print("📡 Navigating to form page...")
        
        async for event in streaming.stream_tool_call(
            "browseruse",
            "navigate", 
            {"url": "https://httpbin.org/forms/post"},
            session_id
        ):
            if event.get("type") == "success":
                print("✅ Form page loaded")
                break
        
        # Now fill out form fields with streaming
        form_fields = [
            {"selector": "#custname", "text": "John Doe", "label": "Name"},
            {"selector": "#custtel", "text": "555-0123", "label": "Phone"},
            {"selector": "#custemail", "text": "john@example.com", "label": "Email"}
        ]
        
        for field in form_fields:
            print(f"\n📝 Filling {field['label']} field...")
            
            async for event in streaming.stream_tool_call(
                "browseruse",
                "type_text",
                {"selector": field["selector"], "text": field["text"]},
                session_id
            ):
                event_type = event.get("type")
                message = event.get("message", "")
                progress = event.get("progress")
                
                if event_type == "progress":
                    if progress:
                        progress_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
                        print(f"    📊 {message} [{progress_bar}] {progress}%")
                    else:
                        print(f"    📊 {message}")
                elif event_type == "success":
                    print(f"    ✅ {field['label']} field filled successfully")
                elif event_type == "error":
                    print(f"    ❌ Error filling {field['label']}: {event.get('error')}")
        
        print("🎉 Form filling completed!")
        
    except Exception as e:
        print(f"❌ Form interaction streaming error: {e}")


async def example_4_streaming_screenshot(session_id: str):
    """Example 4: Stream screenshot capture with progress"""
    print(f"\n📸 Example 4: Streaming Screenshot Capture")
    print("=" * 50)
    
    if not session_id:
        print("❌ No session available for screenshot")
        return
    
    streaming = OpenMCPStreaming()
    
    try:
        print("📡 Capturing screenshot with real-time updates...")
        
        async for event in streaming.stream_tool_call(
            "browseruse",
            "take_screenshot",
            {},
            session_id
        ):
            event_type = event.get("type")
            message = event.get("message", "")
            progress = event.get("progress")
            
            if event_type == "start":
                print(f"🟢 {message}")
            elif event_type == "progress":
                if progress:
                    progress_bar = "█" * int(progress / 5) + "░" * (20 - int(progress / 5))
                    print(f"📊 {message} [{progress_bar}] {progress}%")
                else:
                    print(f"📊 {message}")
            elif event_type == "success":
                result = event.get("result", {})
                screenshot_size = len(result.get("screenshot", ""))
                print(f"✅ {message}")
                print(f"📏 Screenshot size: {screenshot_size:,} characters (base64)")
                
                # Save screenshot to file
                if screenshot_size > 0:
                    import base64
                    screenshot_data = base64.b64decode(result["screenshot"])
                    with open("streaming_screenshot.png", "wb") as f:
                        f.write(screenshot_data)
                    print("💾 Screenshot saved as: streaming_screenshot.png")
                    
            elif event_type == "error":
                print(f"❌ Error: {event.get('error')}")
            elif event_type == "complete":
                print(f"🎯 {message}")
                
    except Exception as e:
        print(f"❌ Screenshot streaming error: {e}")


async def example_5_streaming_cleanup(session_id: str):
    """Example 5: Stream session cleanup"""
    print(f"\n🧹 Example 5: Streaming Session Cleanup")
    print("=" * 50)
    
    if not session_id:
        print("❌ No session available for cleanup")
        return
    
    streaming = OpenMCPStreaming()
    
    try:
        print("📡 Closing browser session...")
        
        async for event in streaming.stream_tool_call(
            "browseruse",
            "close_session",
            {},
            session_id
        ):
            event_type = event.get("type")
            message = event.get("message", "")
            
            if event_type == "start":
                print(f"🟢 {message}")
            elif event_type == "success":
                print(f"✅ Session closed successfully")
            elif event_type == "error":
                print(f"❌ Error: {event.get('error')}")
            elif event_type == "complete":
                print(f"🎯 {message}")
                
    except Exception as e:
        print(f"❌ Cleanup streaming error: {e}")


async def example_6_parallel_streaming():
    """Example 6: Multiple parallel streaming operations"""
    print(f"\n🔄 Example 6: Parallel Streaming Operations")
    print("=" * 50)
    
    streaming = OpenMCPStreaming()
    
    async def create_and_use_session(session_num: int):
        """Create and use a browser session"""
        print(f"📡 Session {session_num}: Creating browser session...")
        
        session_id = None
        try:
            # Create session
            async for event in streaming.stream_tool_call(
                "browseruse",
                "create_session",
                {"headless": True}
            ):
                if event.get("type") == "success":
                    session_id = event.get("result", {}).get("session_id")
                    print(f"✅ Session {session_num}: Created {session_id[:8]}...")
                    break
            
            if session_id:
                # Navigate
                print(f"🌐 Session {session_num}: Navigating...")
                async for event in streaming.stream_tool_call(
                    "browseruse",
                    "navigate",
                    {"url": f"https://httpbin.org/status/200"},
                    session_id
                ):
                    if event.get("type") == "success":
                        result = event.get("result", {})
                        print(f"✅ Session {session_num}: Loaded {result.get('title', 'page')}")
                        break
                
                # Cleanup
                async for event in streaming.stream_tool_call(
                    "browseruse",
                    "close_session",
                    {},
                    session_id
                ):
                    if event.get("type") == "success":
                        print(f"🧹 Session {session_num}: Cleaned up")
                        break
        
        except Exception as e:
            print(f"❌ Session {session_num} error: {e}")
    
    # Run 3 sessions in parallel
    tasks = [
        create_and_use_session(i)
        for i in range(1, 4)
    ]
    
    await asyncio.gather(*tasks)
    print("🎉 All parallel sessions completed!")


async def check_sse_support():
    """Check if SSE streaming is supported"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:9000/api/v1/services", timeout=5.0)
            if response.status_code == 200:
                services = response.json()
                print("🔧 SSE Streaming Support:")
                print("   ✅ Server is running")
                print("   ✅ SSE endpoints available")
                print(f"   📊 Available services: {', '.join(services.get('available_services', []))}")
                return True
            else:
                print("❌ Cannot check SSE support")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to OpenMCP server: {e}")
        print("🚀 Start it with: openmcp serve")
        return False


async def main():
    """Run all SSE streaming examples"""
    print("📡 OpenMCP Server-Sent Events (SSE) Streaming Examples")
    print("🏠 No API key needed - running from localhost!")
    print("=" * 70)
    
    # Check if server supports SSE
    if not await check_sse_support():
        return
    
    print()
    
    try:
        # Example 1: Create session with streaming
        session_id = await example_1_streaming_browser_session()
        
        if session_id:
            # Example 2: Stream navigation
            await example_2_streaming_navigation(session_id)
            
            # Example 3: Stream form interaction
            await example_3_streaming_form_interaction(session_id)
            
            # Example 4: Stream screenshot
            await example_4_streaming_screenshot(session_id)
            
            # Example 5: Stream cleanup
            await example_5_streaming_cleanup(session_id)
        
        # Example 6: Parallel streaming (independent sessions)
        await example_6_parallel_streaming()
        
        print(f"\n🎉 All SSE streaming examples completed!")
        print(f"📁 Check streaming_screenshot.png for captured screenshot")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Streaming interrupted by user")
    except Exception as e:
        print(f"❌ Streaming examples failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())