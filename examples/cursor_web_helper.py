"""
Web Automation Helper for Cursor AI
Add this file to your project to give Cursor web automation capabilities.

Usage:
1. Start openmcp server: `openmcp serve`
2. Get API key from: `openmcp init-config`
3. Set API_KEY below or use environment variable
4. Ask Cursor to generate web automation scripts using this helper!
"""

import httpx
import asyncio
import base64
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

# Set your API key here or use environment variable
API_KEY = os.getenv("OPENMCP_API_KEY", "bmcp_your-api-key-here")

class CursorWebHelper:
    """
    Web automation helper that Cursor can use to:
    - Navigate websites
    - Fill forms  
    - Take screenshots
    - Extract data
    - Test web applications
    
    Example usage in Cursor:
    
    # Ask Cursor: "Create a script that tests the login form on example.com"
    # Cursor will generate:
    
    async def test_login():
        helper = CursorWebHelper()
        await helper.start_browser()
        await helper.navigate("https://example.com/login")
        await helper.type_text("#email", "test@example.com")
        await helper.type_text("#password", "password123")
        await helper.click("#login-button")
        await helper.screenshot("login_test.png")
        await helper.close_browser()
    """
    
    def __init__(self, api_key: str = None, base_url: str = "http://localhost:8000"):
        self.api_key = api_key or API_KEY
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.session_id: Optional[str] = None
        
        # Create screenshots directory
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
    
    async def start_browser(self, headless: bool = True, timeout: int = 30) -> str:
        """Start a new browser session."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/browseruse/call",
                headers=self.headers,
                json={
                    "tool_name": "create_session",
                    "arguments": {"headless": headless, "timeout": timeout}
                }
            )
            result = response.json()
            if result["success"]:
                self.session_id = result["result"]["session_id"]
                print(f"✅ Browser session started: {self.session_id}")
                return self.session_id
            raise Exception(f"Failed to start browser: {result.get('error')}")
    
    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL."""
        if not self.session_id:
            await self.start_browser()
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/browseruse/call",
                headers=self.headers,
                json={
                    "tool_name": "navigate",
                    "arguments": {"url": url},
                    "session_id": self.session_id
                }
            )
            result = response.json()
            if result["success"]:
                print(f"✅ Navigated to: {url}")
                print(f"Page title: {result['result'].get('title', 'Unknown')}")
            return result
    
    async def find_elements(self, selector: str, by: str = "css") -> List[Dict]:
        """Find elements on the page."""
        if not self.session_id:
            raise Exception("No browser session. Call start_browser() first.")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/browseruse/call",
                headers=self.headers,
                json={
                    "tool_name": "find_elements",
                    "arguments": {"selector": selector, "by": by},
                    "session_id": self.session_id
                }
            )
            result = response.json()
            if result["success"]:
                elements = result["result"].get("elements", [])
                print(f"✅ Found {len(elements)} elements matching '{selector}'")
                return elements
            return []
    
    async def click(self, selector: str, by: str = "css") -> bool:
        """Click an element."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/browseruse/call",
                headers=self.headers,
                json={
                    "tool_name": "click_element",
                    "arguments": {"selector": selector, "by": by},
                    "session_id": self.session_id
                }
            )
            result = response.json()
            if result["success"]:
                print(f"✅ Clicked: {selector}")
                return True
            print(f"❌ Click failed: {result.get('error')}")
            return False
    
    async def type_text(self, selector: str, text: str, by: str = "css") -> bool:
        """Type text into an input field."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/browseruse/call",
                headers=self.headers,
                json={
                    "tool_name": "type_text",
                    "arguments": {"selector": selector, "text": text, "by": by},
                    "session_id": self.session_id
                }
            )
            result = response.json()
            if result["success"]:
                print(f"✅ Typed '{text}' into {selector}")
                return True
            print(f"❌ Type failed: {result.get('error')}")
            return False
    
    async def screenshot(self, filename: str = None) -> str:
        """Take a screenshot and save it."""
        if not filename:
            from datetime import datetime
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        filepath = self.screenshots_dir / filename
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/browseruse/call",
                headers=self.headers,
                json={
                    "tool_name": "take_screenshot",
                    "arguments": {},
                    "session_id": self.session_id
                }
            )
            result = response.json()
            if result["success"]:
                screenshot_data = base64.b64decode(result["result"]["screenshot"])
                with open(filepath, "wb") as f:
                    f.write(screenshot_data)
                print(f"✅ Screenshot saved: {filepath}")
                return str(filepath)
            raise Exception(f"Screenshot failed: {result.get('error')}")
    
    async def get_page_info(self) -> Dict[str, Any]:
        """Get current page information."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/browseruse/call",
                headers=self.headers,
                json={
                    "tool_name": "get_page_info",
                    "arguments": {},
                    "session_id": self.session_id
                }
            )
            result = response.json()
            if result["success"]:
                return result["result"]
            return {}
    
    async def close_browser(self):
        """Close the browser session."""
        if not self.session_id:
            return
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/browseruse/call",
                headers=self.headers,
                json={
                    "tool_name": "close_session",
                    "arguments": {},
                    "session_id": self.session_id
                }
            )
            result = response.json()
            if result["success"]:
                print(f"✅ Browser session closed: {self.session_id}")
            self.session_id = None


# Convenience functions for common tasks
async def quick_screenshot(url: str, filename: str = None, api_key: str = None) -> str:
    """Quick function to take a screenshot of any URL."""
    helper = CursorWebHelper(api_key)
    try:
        await helper.start_browser()
        await helper.navigate(url)
        await asyncio.sleep(2)  # Wait for page load
        return await helper.screenshot(filename)
    finally:
        await helper.close_browser()


async def test_form(url: str, form_data: Dict[str, str], api_key: str = None) -> bool:
    """Quick function to test form submission."""
    helper = CursorWebHelper(api_key)
    try:
        await helper.start_browser()
        await helper.navigate(url)
        
        # Fill form fields
        for selector, value in form_data.items():
            await helper.type_text(selector, value)
        
        # Take screenshot before submission
        await helper.screenshot("form_filled.png")
        return True
    finally:
        await helper.close_browser()


# Example functions that Cursor can learn from and generate similar ones
async def example_login_test():
    """Example: Test a login form."""
    helper = CursorWebHelper()
    try:
        await helper.start_browser()
        await helper.navigate("https://httpbin.org/forms/post")
        
        # Fill login form
        await helper.type_text("input[name='custname']", "testuser")
        await helper.type_text("input[name='custemail']", "test@example.com")
        
        # Take screenshot
        await helper.screenshot("login_form.png")
        
        # Click submit (commented out to avoid actual submission)
        # await helper.click("input[type='submit']")
        
        print("✅ Login test completed")
        
    finally:
        await helper.close_browser()


async def example_web_scraping():
    """Example: Scrape data from a website."""
    helper = CursorWebHelper()
    try:
        await helper.start_browser()
        await helper.navigate("https://httpbin.org")
        
        # Get page info
        page_info = await helper.get_page_info()
        print(f"Page title: {page_info.get('title')}")
        
        # Find elements
        links = await helper.find_elements("a")
        print(f"Found {len(links)} links on the page")
        
        # Take screenshot
        await helper.screenshot("scraped_page.png")
        
        return {"title": page_info.get('title'), "link_count": len(links)}
        
    finally:
        await helper.close_browser()


async def example_multi_page_test():
    """Example: Test multiple pages in sequence."""
    pages_to_test = [
        "https://httpbin.org",
        "https://httpbin.org/forms/post",
        "https://httpbin.org/html"
    ]
    
    helper = CursorWebHelper()
    try:
        await helper.start_browser()
        
        for i, url in enumerate(pages_to_test):
            print(f"\n🔍 Testing page {i+1}: {url}")
            await helper.navigate(url)
            await asyncio.sleep(1)  # Wait for page load
            await helper.screenshot(f"page_{i+1}.png")
            
            # Get page info
            page_info = await helper.get_page_info()
            print(f"Title: {page_info.get('title', 'No title')}")
        
        print("✅ Multi-page test completed")
        
    finally:
        await helper.close_browser()


# Main demo function
async def demo():
    """
    Demo function showing various web automation capabilities.
    
    Run this to see openmcp in action, or ask Cursor to generate
    similar functions for your specific use cases!
    """
    print("🚀 openmcp + Cursor Web Automation Demo")
    print("=" * 50)
    
    # Check if API key is set
    if API_KEY == "bmcp_your-api-key-here":
        print("❌ Please set your API key!")
        print("1. Run: openmcp init-config")
        print("2. Copy the API key and set it in this file or as OPENMCP_API_KEY environment variable")
        return
    
    try:
        # Test 1: Simple screenshot
        print("\n📸 Test 1: Taking a screenshot")
        screenshot_path = await quick_screenshot("https://httpbin.org", "demo_screenshot.png")
        print(f"Screenshot saved: {screenshot_path}")
        
        # Test 2: Form interaction
        print("\n📝 Test 2: Form interaction demo")
        await example_login_test()
        
        # Test 3: Web scraping
        print("\n🔍 Test 3: Web scraping demo")
        scrape_result = await example_web_scraping()
        print(f"Scraping result: {scrape_result}")
        
        print("\n🎉 Demo completed successfully!")
        print("\n🎯 Now ask Cursor to:")
        print("  - 'Create a script that tests our contact form'")
        print("  - 'Build a web scraper for product prices'")
        print("  - 'Generate automated tests for our login flow'")
        print("  - 'Take screenshots of all pages on our website'")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure openmcp server is running: openmcp serve")
        print("2. Check your API key is correct")
        print("3. Ensure you have internet connection")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo())
