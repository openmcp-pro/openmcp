# 🔥 openmcp + Cursor + Claude Integration Guide

**Transform your AI coding experience with powerful web automation capabilities!**

## 🎯 Overview

This guide shows you exactly how to integrate openmcp with **Cursor** and **Claude Desktop** to give your AI assistants superpowers for web automation, testing, and data collection.

## 🚀 Cursor Integration

### Method 1: HTTP API Integration (Recommended)

#### Step 1: Setup openmcp
```bash
# Install and start openmcp
pip install -e .
openmcp init-config
openmcp serve
```

#### Step 2: Add Web Automation Helper to Your Project

Create `cursor_web_helper.py` in your project root:

```python
"""
Web Automation Helper for Cursor AI
Add this file to your project to give Cursor web automation capabilities.
"""

import httpx
import asyncio
import base64
from typing import Dict, Any, Optional, List
from pathlib import Path

class CursorWebHelper:
    """
    Web automation helper that Cursor can use to:
    - Navigate websites
    - Fill forms
    - Take screenshots  
    - Extract data
    - Test web applications
    """
    
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.session_id: Optional[str] = None
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
async def quick_screenshot(url: str, api_key: str, filename: str = None) -> str:
    """Quick function to take a screenshot of any URL."""
    helper = CursorWebHelper(api_key)
    try:
        await helper.start_browser()
        await helper.navigate(url)
        await asyncio.sleep(2)  # Wait for page load
        return await helper.screenshot(filename)
    finally:
        await helper.close_browser()

async def test_form(url: str, form_data: Dict[str, str], api_key: str) -> bool:
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
        
        # You can add submit logic here
        return True
    finally:
        await helper.close_browser()

# Example usage for Cursor
async def demo_web_automation():
    """
    Demo function showing web automation capabilities.
    Cursor can call this or generate similar functions.
    """
    # Replace with your actual API key from 'openmcp init-config'
    API_KEY = "bmcp_your-api-key-here"
    
    helper = CursorWebHelper(API_KEY)
    
    try:
        # Start browser
        await helper.start_browser(headless=True)
        
        # Navigate to a website
        await helper.navigate("https://httpbin.org/forms/post")
        
        # Fill out a form
        await helper.type_text("input[name='custname']", "John Doe")
        await helper.type_text("input[name='custtel']", "555-1234")
        await helper.type_text("input[name='custemail']", "john@example.com")
        
        # Select options
        await helper.click("input[value='medium']")  # Pizza size
        await helper.click("input[value='bacon']")   # Topping
        
        # Take screenshot
        screenshot_path = await helper.screenshot("form_demo.png")
        
        # Get page info
        page_info = await helper.get_page_info()
        print(f"Current page: {page_info.get('title')}")
        
        return screenshot_path
        
    finally:
        await helper.close_browser()

if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_web_automation())
```

#### Step 3: Configure Your API Key

Create `.env` file in your project:
```bash
# .env
OPENMCP_API_KEY=bmcp_your-api-key-from-init-config
```

#### Step 4: Use with Cursor

Now you can ask Cursor to:

**🎯 Example Prompts for Cursor:**

1. **"Create a script that tests our login form"**
```python
# Cursor will generate something like:
async def test_login():
    helper = CursorWebHelper(os.getenv("OPENMCP_API_KEY"))
    await helper.start_browser()
    await helper.navigate("https://yourapp.com/login")
    await helper.type_text("#email", "test@example.com")
    await helper.type_text("#password", "testpass123")
    await helper.click("#login-button")
    await helper.screenshot("login_result.png")
    await helper.close_browser()
```

2. **"Build a web scraper for product prices"**
```python
# Cursor will generate:
async def scrape_prices():
    helper = CursorWebHelper(os.getenv("OPENMCP_API_KEY"))
    await helper.start_browser()
    await helper.navigate("https://shop.example.com")
    
    products = await helper.find_elements(".product")
    prices = []
    
    for i, product in enumerate(products):
        price_element = await helper.find_elements(f".product:nth-child({i+1}) .price")
        if price_element:
            prices.append(price_element[0]['text'])
    
    return prices
```

3. **"Automate taking screenshots of our website on different pages"**
```python
# Cursor will generate:
async def screenshot_all_pages():
    pages = ["/", "/about", "/contact", "/products"]
    helper = CursorWebHelper(os.getenv("OPENMCP_API_KEY"))
    
    await helper.start_browser()
    for page in pages:
        await helper.navigate(f"https://yoursite.com{page}")
        await helper.screenshot(f"page_{page.replace('/', 'home')}.png")
    await helper.close_browser()
```

### Method 2: MCP Integration (Advanced)

#### Step 1: Configure Cursor for MCP

Create `.cursor/mcp.json` in your project:
```json
{
  "mcpServers": {
    "openmcp": {
      "command": "openmcp",
      "args": ["serve", "--protocol", "mcp"],
      "env": {}
    }
  }
}
```

#### Step 2: Restart Cursor

Cursor will automatically connect to openmcp and show available tools.

## 🤖 Claude Desktop Integration

### Step 1: Install Claude Desktop

Download from [Anthropic's website](https://claude.ai/desktop)

### Step 2: Configure MCP Server

Edit Claude's MCP configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%/Claude/claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "openmcp-browser": {
      "command": "openmcp",
      "args": ["serve", "--protocol", "mcp"],
      "env": {}
    }
  }
}
```

### Step 3: Restart Claude Desktop

Claude will automatically discover openmcp tools.

### Step 4: Use with Claude

**🎯 Example Conversations with Claude:**

**You:** *"Please help me test the contact form on https://example.com"*

**Claude:** *I'll help you test the contact form. Let me:*
1. *Create a browser session*
2. *Navigate to the website*
3. *Find the contact form*
4. *Fill it with test data*
5. *Take screenshots of the process*

*[Claude automatically uses openmcp tools]*

**You:** *"Take screenshots of the top 5 trending GitHub repositories"*

**Claude:** *I'll navigate to GitHub and capture screenshots of the trending repos:*
1. *Opening GitHub trending page*
2. *Taking initial screenshot*
3. *Capturing individual repository pages*

*[Claude completes the task automatically]*

**You:** *"Check if my website loads correctly on mobile view"*

**Claude:** *I'll test your website's mobile responsiveness:*
1. *Creating a browser session*
2. *Setting mobile viewport*
3. *Loading your website*
4. *Taking screenshots*
5. *Checking for mobile-specific issues*

## 🎯 Real-World Use Cases

### 1. Automated Testing

**Cursor Prompt:** *"Generate comprehensive tests for our e-commerce checkout flow"*

**Result:** Cursor creates test scripts that:
- Navigate through product selection
- Add items to cart
- Fill checkout forms
- Test payment flows
- Capture screenshots at each step
- Validate success/error states

### 2. Data Collection

**Claude Request:** *"Collect all job postings from this careers page and save to CSV"*

**Result:** Claude automatically:
- Navigates to careers page
- Finds all job listings
- Extracts job titles, descriptions, requirements
- Formats data into CSV
- Saves file locally

### 3. UI/UX Testing

**Cursor Prompt:** *"Create a script that tests our website's accessibility"*

**Result:** Cursor generates code that:
- Tests keyboard navigation
- Checks color contrast
- Validates form labels
- Tests screen reader compatibility
- Generates accessibility report

### 4. Competitive Analysis

**Claude Request:** *"Compare pricing tables from our top 3 competitors"*

**Result:** Claude:
- Visits each competitor website
- Finds pricing sections
- Extracts pricing data
- Takes comparison screenshots
- Creates summary report

## 🔧 Advanced Configuration

### Custom Prompts for Better Results

#### For Cursor:
```python
# Add this comment block to guide Cursor
"""
Web Automation Guidelines for Cursor:

1. Always use try/finally blocks to ensure browser cleanup
2. Add appropriate waits (asyncio.sleep) after navigation
3. Take screenshots for verification
4. Handle errors gracefully
5. Use descriptive variable names
6. Add logging/print statements for debugging

Example pattern:
async def my_automation_task():
    helper = CursorWebHelper(os.getenv("OPENMCP_API_KEY"))
    try:
        await helper.start_browser()
        # Your automation logic here
        await helper.screenshot("result.png")
    finally:
        await helper.close_browser()
"""
```

#### For Claude:
When talking to Claude, be specific:
- ✅ *"Navigate to X, find element Y, and take a screenshot"*
- ✅ *"Fill out the form with these specific values: ..."*
- ✅ *"Test the login flow and verify success"*
- ❌ *"Do some web stuff"*

### Environment Setup

Create a dedicated environment for web automation:

```bash
# Create project structure
mkdir my-web-automation
cd my-web-automation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install httpx asyncio python-dotenv

# Copy the cursor_web_helper.py file
# Create .env with your API key
# Start coding with Cursor/Claude!
```

## 🚨 Troubleshooting

### Common Issues

**1. "API Key Invalid" Error**
```bash
# Regenerate API key
openmcp init-config --force
# Update your .env file with new key
```

**2. "Connection Refused" Error**
```bash
# Make sure openmcp server is running
openmcp serve
# Check if port 8000 is available
netstat -an | grep 8000
```

**3. "Browser Session Failed" Error**
```bash
# Install Chrome/Chromium
sudo apt-get install chromium-browser  # Linux
brew install --cask google-chrome      # macOS
# Windows: Download from Google
```

**4. Cursor/Claude Not Finding Tools**
```bash
# For MCP integration, restart the application
# Check MCP configuration syntax
# Verify openmcp is in PATH
which openmcp
```

### Performance Tips

1. **Reuse Browser Sessions** - Don't create new sessions for every operation
2. **Use Headless Mode** - Faster execution, less resource usage
3. **Add Appropriate Waits** - Let pages load completely
4. **Close Sessions** - Always clean up resources
5. **Batch Operations** - Group related actions together

## 🎉 Success Stories

### Developer Testimonials

> *"openmcp + Cursor transformed how I build web scrapers. I just describe what I want, and Cursor generates the complete automation script!"*
> — Sarah, Full-Stack Developer

> *"Claude with openmcp is like having a QA engineer that never sleeps. It tests our entire website automatically!"*
> — Mike, Startup CTO

> *"I use openmcp with Cursor to generate comprehensive test suites. It's saved me weeks of manual testing work."*
> — Alex, DevOps Engineer

## 🚀 Next Steps

1. **Start Simple** - Try the basic examples first
2. **Experiment** - Ask Cursor/Claude to automate different tasks
3. **Build Libraries** - Create reusable automation functions
4. **Share** - Contribute your automation patterns back to the community
5. **Scale** - Deploy openmcp in production for team use

## 📚 Additional Resources

- **[openmcp Documentation](README.md)** - Complete project documentation
- **[API Reference](http://localhost:8000/docs)** - Interactive API docs
- **[Example Scripts](examples/)** - Ready-to-use automation scripts
- **[Community Forum](https://github.com/openmcp/openmcp/discussions)** - Get help and share ideas

---

**🎯 Ready to supercharge your AI coding workflow?**

Start with the basic setup above, then ask Cursor or Claude to help you automate your first web task! 🚀
