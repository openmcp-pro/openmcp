#!/usr/bin/env python3
"""
Super Simple openmcp Usage Examples

This shows the new super easy interface:
    mcp = openmcp.MCP("browseruse")

No more complex HTTP requests or MCP protocol details!
"""

import asyncio
import openmcp


async def example_1_basic_usage():
    """Example 1: Basic MCP usage - the new simple way!"""
    print("🚀 Example 1: Basic MCP Usage")
    print("=" * 40)
    
    # Create MCP instance - auto-detects API key!
    mcp = openmcp.MCP("browseruse")
    
    # Create a browser session
    session = await mcp.create_session(headless=True)
    
    try:
        # Navigate to a website
        await session.navigate("https://httpbin.org")
        
        # Get page info
        page_info = await session.page_info()
        print(f"📄 Page title: {page_info.get('title', 'No title')}")
        
        # Take a screenshot
        screenshot_path = await session.screenshot("httpbin.png")
        print(f"📸 Screenshot saved: {screenshot_path}")
        
        # Find elements
        links = await session.find("a")
        print(f"🔗 Found {len(links)} links on the page")
        
    finally:
        # Clean up
        await session.close()
    
    print("✅ Example 1 completed!\n")


async def example_2_context_manager():
    """Example 2: Even simpler with context manager!"""
    print("🚀 Example 2: Context Manager (Recommended)")
    print("=" * 50)
    
    # Super simple - automatically handles session cleanup!
    async with openmcp.browser() as browser:
        # Navigate to a form
        await browser.navigate("https://httpbin.org/forms/post")
        
        # Fill out the form
        await browser.type("input[name='custname']", "John Doe")
        await browser.type("input[name='custtel']", "555-1234")
        await browser.type("input[name='custemail']", "john@example.com")
        
        # Select radio button
        await browser.click("input[value='medium']")
        
        # Take screenshot
        screenshot_path = await browser.screenshot("form_filled.png")
        print(f"📸 Form screenshot: {screenshot_path}")
        
        # Get page info
        page_info = await browser.page_info()
        print(f"📄 Current page: {page_info.get('url', 'Unknown')}")
    
    # Session automatically closed here!
    print("✅ Example 2 completed!\n")


async def example_3_one_liners():
    """Example 3: One-liner convenience functions!"""
    print("🚀 Example 3: One-Liner Functions")
    print("=" * 40)
    
    # One-liner screenshot
    screenshot_path = await openmcp.screenshot("https://httpbin.org", "oneliner.png")
    print(f"📸 One-liner screenshot: {screenshot_path}")
    
    # One-liner form test
    form_data = {
        "input[name='custname']": "Test User",
        "input[name='custemail']": "test@example.com"
    }
    
    form_screenshot = await openmcp.test_form(
        "https://httpbin.org/forms/post", 
        form_data
    )
    print(f"📝 Form test screenshot: {form_screenshot}")
    
    print("✅ Example 3 completed!\n")


async def example_4_multiple_operations():
    """Example 4: Multiple operations in one session."""
    print("🚀 Example 4: Multiple Operations")
    print("=" * 40)
    
    mcp = openmcp.MCP("browseruse")
    
    # Quick navigation returns a session for further use
    session = await mcp.quick_navigate("https://httpbin.org")
    
    try:
        # Take initial screenshot
        await session.screenshot("initial.png")
        
        # Navigate to different pages
        pages = ["/html", "/json", "/xml"]
        
        for i, page in enumerate(pages):
            await session.navigate(f"https://httpbin.org{page}")
            await session.screenshot(f"page_{i+1}.png")
            
            page_info = await session.page_info()
            print(f"📄 Page {i+1}: {page_info.get('title', 'No title')}")
    
    finally:
        await session.close()
    
    print("✅ Example 4 completed!\n")


async def example_5_error_handling():
    """Example 5: Proper error handling."""
    print("🚀 Example 5: Error Handling")
    print("=" * 30)
    
    try:
        async with openmcp.browser() as browser:
            # This will work
            await browser.navigate("https://httpbin.org")
            print("✅ Navigation successful")
            
            # This might fail
            try:
                await browser.click("#nonexistent-button")
            except openmcp.MCPError as e:
                print(f"⚠️  Expected error: {e}")
            
            # Take screenshot anyway
            await browser.screenshot("error_handling.png")
            print("📸 Screenshot taken despite error")
    
    except openmcp.MCPError as e:
        print(f"❌ MCP Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("✅ Example 5 completed!\n")


async def demo_for_cursor_and_claude():
    """
    Demo function perfect for Cursor and Claude to learn from!
    
    This shows the patterns that AI assistants can use to generate
    web automation scripts automatically.
    """
    print("🤖 Demo for Cursor & Claude")
    print("=" * 30)
    
    # Pattern 1: Simple automation
    async with openmcp.browser() as browser:
        await browser.navigate("https://httpbin.org")
        await browser.screenshot("demo.png")
        print("✅ Simple automation completed")
    
    # Pattern 2: Form interaction
    async with openmcp.browser() as browser:
        await browser.navigate("https://httpbin.org/forms/post")
        
        # Fill form fields
        await browser.type("input[name='custname']", "AI Assistant")
        await browser.type("input[name='custemail']", "ai@example.com")
        
        # Select options
        await browser.click("input[value='large']")
        await browser.click("input[value='cheese']")
        
        await browser.screenshot("ai_form.png")
        print("✅ Form interaction completed")
    
    # Pattern 3: Data extraction
    async with openmcp.browser() as browser:
        await browser.navigate("https://httpbin.org")
        
        # Find all links
        links = await browser.find("a")
        print(f"🔗 Found {len(links)} links:")
        
        for i, link in enumerate(links[:5]):  # Show first 5
            print(f"  {i+1}. {link.get('text', 'No text')}")
        
        print("✅ Data extraction completed")
    
    print("🎉 All demos completed!")


async def main():
    """Main function - run all examples."""
    print("🎯 openmcp Super Simple Interface Demo")
    print("=" * 60)
    
    # Check if server is running
    if not await openmcp.ensure_server_running():
        print("\n💡 To start the server, run:")
        print("   openmcp serve")
        print("\n💡 To get an API key, run:")
        print("   openmcp init-config")
        return
    
    print("✅ openmcp server is running!\n")
    
    try:
        # Run all examples
        await example_1_basic_usage()
        await example_2_context_manager()
        await example_3_one_liners()
        await example_4_multiple_operations()
        await example_5_error_handling()
        await demo_for_cursor_and_claude()
        
        print("🎉 All examples completed successfully!")
        print("\n🎯 Now you can use openmcp like this:")
        print("   mcp = openmcp.MCP('browseruse')")
        print("   session = await mcp.create_session()")
        print("   await session.navigate('https://example.com')")
        print("\n🤖 Perfect for Cursor and Claude to generate automatically!")
        
    except openmcp.MCPError as e:
        print(f"❌ MCP Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure openmcp server is running: openmcp serve")
        print("   2. Check your API key: openmcp init-config")
        print("   3. Verify server health: curl http://localhost:8000/health")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
