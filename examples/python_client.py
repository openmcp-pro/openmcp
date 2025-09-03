#!/usr/bin/env python3
"""
Example Python client for openmcp.

This example demonstrates how to use the openmcp API to control a browser
and perform web automation tasks.
"""

import asyncio
import base64
from pathlib import Path
from typing import Dict, Any, Optional

import httpx


class OpenMCPClient:
    """Python client for openmcp API."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check server health."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
    
    async def list_services(self) -> Dict[str, Any]:
        """List available services."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/services",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def list_service_tools(self, service_name: str) -> Dict[str, Any]:
        """List tools for a specific service."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/services/{service_name}/tools",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def call_tool(
        self, 
        service_name: str, 
        tool_name: str, 
        arguments: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call a tool on a service."""
        payload = {
            "tool_name": tool_name,
            "arguments": arguments
        }
        if session_id:
            payload["session_id"] = session_id
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/{service_name}/call",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()


class BrowserAutomation:
    """High-level browser automation using openmcp."""
    
    def __init__(self, client: OpenMCPClient):
        self.client = client
        self.session_id: Optional[str] = None
    
    async def create_session(self, headless: bool = True, timeout: int = 30) -> str:
        """Create a new browser session."""
        result = await self.client.call_tool(
            "browseruse",
            "create_session",
            {"headless": headless, "timeout": timeout}
        )
        
        if not result["success"]:
            raise Exception(f"Failed to create session: {result.get('error')}")
        
        self.session_id = result["result"]["session_id"]
        print(f"Created browser session: {self.session_id}")
        return self.session_id
    
    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL."""
        if not self.session_id:
            raise Exception("No active session. Create a session first.")
        
        result = await self.client.call_tool(
            "browseruse",
            "navigate",
            {"url": url},
            self.session_id
        )
        
        if not result["success"]:
            raise Exception(f"Failed to navigate: {result.get('error')}")
        
        return result["result"]
    
    async def find_elements(self, selector: str, by: str = "css") -> list:
        """Find elements on the page."""
        if not self.session_id:
            raise Exception("No active session. Create a session first.")
        
        result = await self.client.call_tool(
            "browseruse",
            "find_elements",
            {"selector": selector, "by": by},
            self.session_id
        )
        
        if not result["success"]:
            raise Exception(f"Failed to find elements: {result.get('error')}")
        
        return result["result"]["elements"]
    
    async def click_element(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Click an element."""
        if not self.session_id:
            raise Exception("No active session. Create a session first.")
        
        result = await self.client.call_tool(
            "browseruse",
            "click_element",
            {"selector": selector, "by": by},
            self.session_id
        )
        
        if not result["success"]:
            raise Exception(f"Failed to click element: {result.get('error')}")
        
        return result["result"]
    
    async def type_text(self, selector: str, text: str, by: str = "css") -> Dict[str, Any]:
        """Type text into an element."""
        if not self.session_id:
            raise Exception("No active session. Create a session first.")
        
        result = await self.client.call_tool(
            "browseruse",
            "type_text",
            {"selector": selector, "text": text, "by": by},
            self.session_id
        )
        
        if not result["success"]:
            raise Exception(f"Failed to type text: {result.get('error')}")
        
        return result["result"]
    
    async def take_screenshot(self, save_path: Optional[Path] = None) -> str:
        """Take a screenshot."""
        if not self.session_id:
            raise Exception("No active session. Create a session first.")
        
        result = await self.client.call_tool(
            "browseruse",
            "take_screenshot",
            {},
            self.session_id
        )
        
        if not result["success"]:
            raise Exception(f"Failed to take screenshot: {result.get('error')}")
        
        screenshot_b64 = result["result"]["screenshot"]
        
        if save_path:
            screenshot_data = base64.b64decode(screenshot_b64)
            with open(save_path, "wb") as f:
                f.write(screenshot_data)
            print(f"Screenshot saved to: {save_path}")
        
        return screenshot_b64
    
    async def get_page_info(self) -> Dict[str, Any]:
        """Get current page information."""
        if not self.session_id:
            raise Exception("No active session. Create a session first.")
        
        result = await self.client.call_tool(
            "browseruse",
            "get_page_info",
            {},
            self.session_id
        )
        
        if not result["success"]:
            raise Exception(f"Failed to get page info: {result.get('error')}")
        
        return result["result"]
    
    async def close_session(self) -> None:
        """Close the browser session."""
        if not self.session_id:
            return
        
        result = await self.client.call_tool(
            "browseruse",
            "close_session",
            {},
            self.session_id
        )
        
        if result["success"]:
            print(f"Closed browser session: {self.session_id}")
        else:
            print(f"Failed to close session: {result.get('error')}")
        
        self.session_id = None


async def example_web_search():
    """Example: Perform a web search."""
    # Initialize client (replace with your API key)
    client = OpenMCPClient(api_key="bmcp_your-api-key-here")
    browser = BrowserAutomation(client)
    
    try:
        # Check server health
        health = await client.health_check()
        print(f"Server status: {health['status']}")
        
        # Create browser session
        await browser.create_session(headless=True)
        
        # Navigate to DuckDuckGo
        print("Navigating to DuckDuckGo...")
        await browser.navigate("https://duckduckgo.com")
        
        # Get page info
        page_info = await browser.get_page_info()
        print(f"Page title: {page_info['title']}")
        
        # Find search box and type query
        print("Searching for 'openmcp'...")
        await browser.type_text("input[name='q']", "openmcp")
        
        # Click search button
        await browser.click_element("button[type='submit']")
        
        # Wait a moment for results to load
        await asyncio.sleep(2)
        
        # Take screenshot
        await browser.take_screenshot(Path("search_results.png"))
        
        # Find search results
        results = await browser.find_elements(".result__title")
        print(f"Found {len(results)} search results")
        
        for i, result in enumerate(results[:3]):
            print(f"Result {i+1}: {result['text']}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Clean up
        await browser.close_session()


async def example_form_filling():
    """Example: Fill out a form."""
    client = OpenMCPClient(api_key="bmcp_your-api-key-here")
    browser = BrowserAutomation(client)
    
    try:
        await browser.create_session(headless=False)  # Show browser for demo
        
        # Navigate to a form (example)
        await browser.navigate("https://httpbin.org/forms/post")
        
        # Fill out form fields
        await browser.type_text("input[name='custname']", "John Doe")
        await browser.type_text("input[name='custtel']", "555-1234")
        await browser.type_text("input[name='custemail']", "john@example.com")
        
        # Select pizza size
        await browser.click_element("input[value='medium']")
        
        # Add toppings
        await browser.click_element("input[value='bacon']")
        await browser.click_element("input[value='cheese']")
        
        # Take screenshot before submitting
        await browser.take_screenshot(Path("form_filled.png"))
        
        print("Form filled successfully!")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        await browser.close_session()


async def main():
    """Main example function."""
    print("openmcp Python Client Examples")
    print("=" * 40)
    
    # Example 1: Web search
    print("\n1. Web Search Example")
    await example_web_search()
    
    # Example 2: Form filling (uncomment to run)
    # print("\n2. Form Filling Example")
    # await example_form_filling()


if __name__ == "__main__":
    asyncio.run(main())
