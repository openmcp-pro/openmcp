#!/usr/bin/env python3
"""
Minimal OpenMCP Example - Copy and paste to get started!

No API key needed from localhost.
"""

import asyncio
import openmcp


async def main():
    # Create browser session (no API key needed from localhost!)
    async with openmcp.browser() as browser:
        # Navigate to any website
        await browser.navigate("https://example.com")
        
        # Take a screenshot
        await browser.screenshot("my_screenshot.png")
        
        # Get page title
        page_info = await browser.get_page_info()
        print(f"Page title: {page_info['title']}")
        
        print("✅ Done! Check my_screenshot.png")


# Run it
if __name__ == "__main__":
    asyncio.run(main())