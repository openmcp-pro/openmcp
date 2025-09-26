#!/usr/bin/env python3
"""
Complete examples showing how to use openmcp locally with no authentication required.

Since you're running from localhost, no API key is needed!
"""

import asyncio
import base64
from pathlib import Path
import openmcp


async def example_1_super_simple():
    """Example 1: Super simple interface - recommended for beginners"""
    print("🚀 Example 1: Super Simple Interface")
    print("=" * 50)
    
    # No API key needed from localhost!
    mcp = openmcp.MCP("browseruse")
    
    try:
        # Create a browser session
        session = await mcp.create_session(headless=True)
        print(f"✅ Created browser session: {session.session_id}")
        
        # Navigate to a website
        await session.navigate("https://httpbin.org/forms/post")
        print("✅ Navigated to httpbin form")
        
        # Take a screenshot
        await session.screenshot("simple_example.png")
        print("✅ Screenshot saved as simple_example.png")
        
        # Get page information
        page_info = await session.get_page_info()
        print(f"📄 Page title: {page_info['title']}")
        
        # Close the session
        await session.close()
        print("✅ Browser session closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_2_context_manager():
    """Example 2: Context manager - automatic cleanup"""
    print("\n🔄 Example 2: Context Manager (Recommended)")
    print("=" * 50)
    
    try:
        # Context manager automatically handles session creation and cleanup
        async with openmcp.browser() as browser:
            # Navigate to a demo site
            await browser.navigate("https://example.com")
            print("✅ Navigated to example.com")
            
            # Take a screenshot
            await browser.screenshot("context_example.png")
            print("✅ Screenshot saved as context_example.png")
            
            # Get page info
            page_info = await browser.get_page_info()
            print(f"📄 Current URL: {page_info['url']}")
            print(f"📄 Page title: {page_info['title']}")
            
        # Browser automatically closed when exiting context
        print("✅ Browser automatically closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_3_form_automation():
    """Example 3: Form filling and interaction"""
    print("\n📝 Example 3: Form Automation")
    print("=" * 50)
    
    try:
        async with openmcp.browser() as browser:
            # Navigate to a form
            await browser.navigate("https://httpbin.org/forms/post")
            print("✅ Navigated to test form")
            
            # Fill out the form fields
            await browser.type("#custname", "John Doe")
            print("✅ Entered customer name")
            
            await browser.type("#custtel", "555-1234")
            print("✅ Entered phone number")
            
            await browser.type("#custemail", "john@example.com")
            print("✅ Entered email")
            
            # Select pizza size
            await browser.click("input[value='medium']")
            print("✅ Selected medium pizza")
            
            # Add toppings
            await browser.click("input[value='bacon']")
            await browser.click("input[value='cheese']")
            print("✅ Added bacon and cheese toppings")
            
            # Take screenshot of filled form
            await browser.screenshot("filled_form.png")
            print("✅ Screenshot of filled form saved")
            
            # Note: We're not submitting to avoid spamming the test server
            print("ℹ️  Form filled but not submitted (demo purposes)")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_4_web_scraping():
    """Example 4: Web scraping with element finding"""
    print("\n🔍 Example 4: Web Scraping")
    print("=" * 50)
    
    try:
        async with openmcp.browser() as browser:
            # Navigate to a page with content
            await browser.navigate("https://httpbin.org")
            print("✅ Navigated to httpbin.org")
            
            # Find elements on the page
            links = await browser.find_elements("a")
            print(f"🔗 Found {len(links)} links on the page")
            
            # Print first few links
            for i, link in enumerate(links[:5]):
                print(f"   {i+1}. {link.get('text', 'No text')} -> {link.get('href', 'No href')}")
            
            # Find specific elements
            headings = await browser.find_elements("h1, h2, h3")
            print(f"📑 Found {len(headings)} headings:")
            for heading in headings[:3]:
                print(f"   • {heading.get('text', 'No text')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_5_direct_http_api():
    """Example 5: Direct HTTP API usage (for advanced users)"""
    print("\n🌐 Example 5: Direct HTTP API Usage")
    print("=" * 50)
    
    import httpx
    
    try:
        # No authentication header needed from localhost!
        async with httpx.AsyncClient() as client:
            # Check server health
            response = await client.get("http://localhost:9000/health")
            health = response.json()
            print(f"🏥 Server status: {health['status']}")
            
            # List available services
            response = await client.get("http://localhost:9000/api/v1/services")
            services = response.json()
            print(f"🔧 Available services: {services['available_services']}")
            
            # Create a browser session directly via API
            response = await client.post(
                "http://localhost:9000/api/v1/services/browseruse/call",
                json={
                    "tool_name": "create_session",
                    "arguments": {"headless": True, "timeout": 30}
                }
            )
            result = response.json()
            
            if result["success"]:
                session_id = result["result"]["session_id"]
                print(f"✅ Created session via API: {session_id}")
                
                # Navigate using direct API
                response = await client.post(
                    "http://localhost:9000/api/v1/services/browseruse/call",
                    json={
                        "tool_name": "navigate",
                        "arguments": {"url": "https://example.com"},
                        "session_id": session_id
                    }
                )
                nav_result = response.json()
                
                if nav_result["success"]:
                    print("✅ Navigation successful via direct API")
                
                # Take screenshot via API
                response = await client.post(
                    "http://localhost:9000/api/v1/services/browseruse/call",
                    json={
                        "tool_name": "take_screenshot",
                        "arguments": {},
                        "session_id": session_id
                    }
                )
                screenshot_result = response.json()
                
                if screenshot_result["success"]:
                    # Save screenshot
                    screenshot_data = base64.b64decode(screenshot_result["result"]["screenshot"])
                    with open("api_screenshot.png", "wb") as f:
                        f.write(screenshot_data)
                    print("✅ Screenshot saved via direct API")
                
                # Close session
                response = await client.post(
                    "http://localhost:9000/api/v1/services/browseruse/call",
                    json={
                        "tool_name": "close_session",
                        "arguments": {},
                        "session_id": session_id
                    }
                )
                print("✅ Session closed via API")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_6_one_liners():
    """Example 6: One-liner functions for quick tasks"""
    print("\n⚡ Example 6: One-Liner Functions")
    print("=" * 50)
    
    try:
        # Quick screenshot
        await openmcp.screenshot("https://example.com", "oneliner_screenshot.png")
        print("✅ One-liner screenshot saved")
        
        # Quick form test (if the function exists)
        try:
            await openmcp.test_form("https://httpbin.org/forms/post", {
                "#custname": "Quick Test",
                "#custemail": "test@example.com"
            })
            print("✅ One-liner form test completed")
        except AttributeError:
            print("ℹ️  test_form function not available in this version")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_7_error_handling():
    """Example 7: Proper error handling"""
    print("\n🛡️ Example 7: Error Handling Best Practices")
    print("=" * 50)
    
    try:
        async with openmcp.browser() as browser:
            try:
                # Try to navigate to an invalid URL
                await browser.navigate("https://this-domain-does-not-exist-12345.com")
                print("✅ Navigation successful")
            except Exception as nav_error:
                print(f"⚠️  Navigation failed (expected): {nav_error}")
            
            # Navigate to a working site
            await browser.navigate("https://example.com")
            print("✅ Fallback navigation successful")
            
            try:
                # Try to find non-existent element
                elements = await browser.find_elements("#non-existent-element")
                print(f"🔍 Found {len(elements)} non-existent elements")
            except Exception as find_error:
                print(f"⚠️  Element not found (expected): {find_error}")
            
            # Take final screenshot
            await browser.screenshot("error_handling_example.png")
            print("✅ Final screenshot saved")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def main():
    """Run all examples"""
    print("🎯 OpenMCP Localhost Usage Examples")
    print("🏠 Running from localhost - no API key required!")
    print("=" * 60)
    print()
    
    # Make sure openmcp server is running
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:9000/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ OpenMCP server is running!")
            else:
                print("❌ OpenMCP server returned error status")
                return
    except Exception:
        print("❌ Cannot connect to OpenMCP server at localhost:9000")
        print("   Please start the server with: openmcp serve")
        return
    
    print()
    
    # Run all examples
    examples = [
        example_1_super_simple,
        example_2_context_manager,
        example_3_form_automation,
        example_4_web_scraping,
        example_5_direct_http_api,
        example_6_one_liners,
        example_7_error_handling
    ]
    
    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"❌ Example failed: {e}")
        
        # Small delay between examples
        await asyncio.sleep(1)
    
    print("\n🎉 All examples completed!")
    print("\n📁 Generated files:")
    for file in ["simple_example.png", "context_example.png", "filled_form.png", 
                 "api_screenshot.png", "oneliner_screenshot.png", "error_handling_example.png"]:
        if Path(file).exists():
            print(f"   • {file}")


if __name__ == "__main__":
    asyncio.run(main())