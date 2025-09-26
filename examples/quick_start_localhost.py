#!/usr/bin/env python3
"""
Quick Start Example: Using OpenMCP from localhost (no API key needed!)

This is the simplest way to get started with OpenMCP locally.
"""

import asyncio
import openmcp


async def quick_demo():
    """5-minute demo of OpenMCP capabilities"""
    
    print("🚀 OpenMCP Quick Start - Localhost Demo")
    print("=" * 50)
    print("🏠 No API key needed - running from localhost!")
    print()
    
    try:
        # Super simple - just one line to create a browser!
        async with openmcp.browser() as browser:
            print("✅ Browser session created")
            
            # Navigate to a website
            print("🌐 Navigating to example.com...")
            await browser.navigate("https://example.com")
            
            # Take a screenshot
            print("📸 Taking screenshot...")
            await browser.screenshot("quick_demo.png")
            
            # Get page information
            page_info = await browser.get_page_info()
            print(f"📄 Page title: {page_info['title']}")
            print(f"🔗 Current URL: {page_info['url']}")
            
            # Find some elements
            print("🔍 Finding links on the page...")
            links = await browser.find_elements("a")
            print(f"🔗 Found {len(links)} links")
            
            print("✅ Demo completed successfully!")
            print("📁 Screenshot saved as: quick_demo.png")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure OpenMCP server is running: openmcp serve")


async def form_filling_demo():
    """Demo filling out a web form"""
    
    print("\n📝 Form Filling Demo")
    print("=" * 30)
    
    try:
        async with openmcp.browser() as browser:
            # Go to a test form
            await browser.navigate("https://httpbin.org/forms/post")
            print("📋 Opened test form")
            
            # Fill out the form
            await browser.type("#custname", "John Doe")
            await browser.type("#custtel", "555-0123")
            await browser.type("#custemail", "john@example.com")
            print("✍️  Filled out form fields")
            
            # Select options
            await browser.click("input[value='medium']")  # Pizza size
            await browser.click("input[value='cheese']")  # Topping
            print("☑️  Selected form options")
            
            # Take screenshot of completed form
            await browser.screenshot("form_filled.png")
            print("📸 Screenshot saved: form_filled.png")
            
    except Exception as e:
        print(f"❌ Form demo error: {e}")


async def web_scraping_demo():
    """Demo basic web scraping"""
    
    print("\n🔍 Web Scraping Demo")
    print("=" * 25)
    
    try:
        async with openmcp.browser() as browser:
            # Navigate to a content-rich page
            await browser.navigate("https://httpbin.org")
            
            # Extract headings
            headings = await browser.find_elements("h1, h2, h3")
            print("📑 Page headings found:")
            for i, heading in enumerate(headings[:3], 1):
                text = heading.get('text', 'No text')
                print(f"   {i}. {text}")
            
            # Extract links
            links = await browser.find_elements("a[href]")
            print(f"\n🔗 Found {len(links)} links")
            print("🔗 First few links:")
            for i, link in enumerate(links[:3], 1):
                text = link.get('text', 'No text').strip()
                href = link.get('href', 'No href')
                if text:
                    print(f"   {i}. {text} -> {href}")
            
    except Exception as e:
        print(f"❌ Scraping demo error: {e}")


async def main():
    """Run the quick start examples"""
    
    # Check if server is running
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:9000/health", timeout=3.0)
            if response.status_code != 200:
                raise Exception("Server not healthy")
    except Exception:
        print("❌ OpenMCP server not running!")
        print("🚀 Start it with: openmcp serve")
        print("📖 Or see README.md for setup instructions")
        return
    
    # Run demos
    await quick_demo()
    await form_filling_demo() 
    await web_scraping_demo()
    
    print(f"\n🎉 All demos completed!")
    print(f"📁 Check these generated files:")
    print(f"   • quick_demo.png")
    print(f"   • form_filled.png")


if __name__ == "__main__":
    # Run the quick start demo
    asyncio.run(main())