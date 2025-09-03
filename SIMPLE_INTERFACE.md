# 🎉 Super Simple openmcp Interface

## 🎯 The Problem We Solved

**Before:** Complex HTTP requests and MCP protocol details
```python
# Old way - complex and verbose
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/services/browseruse/call",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "tool_name": "create_session",
            "arguments": {"headless": True}
        }
    )
    result = response.json()
    session_id = result["result"]["session_id"]
    # ... more complex code
```

**After:** Super simple, Pythonic interface
```python
# New way - incredibly simple!
import openmcp

mcp = openmcp.MCP("browseruse")
session = await mcp.create_session()
await session.navigate("https://example.com")
await session.screenshot("page.png")
```

## ✨ What's New

### 🚀 **Simple MCP Creation**
```python
# Just one line!
mcp = openmcp.MCP("browseruse")

# Auto-detects API key from:
# 1. Environment variable OPENMCP_API_KEY
# 2. config.yaml file
# 3. Running server's auth manager
```

### 🔧 **Intuitive Session Management**
```python
# Create and use sessions easily
session = await mcp.create_session(headless=True)
await session.navigate("https://example.com")
await session.click("#button")
await session.type("#input", "text")
await session.screenshot("result.png")
await session.close()
```

### 🎯 **Context Manager (Recommended)**
```python
# Automatic cleanup!
async with openmcp.browser() as browser:
    await browser.navigate("https://example.com")
    await browser.click("#button")
    await browser.screenshot("result.png")
# Session automatically closed
```

### ⚡ **One-Liner Functions**
```python
# Quick screenshot
await openmcp.screenshot("https://example.com", "page.png")

# Quick form test
await openmcp.test_form("https://example.com/form", {
    "#name": "John Doe",
    "#email": "john@example.com"
})
```

## 🎯 Perfect for AI Assistants

### **Cursor Integration**
Ask Cursor: *"Create a script using openmcp to test our login form"*

Cursor generates:
```python
import openmcp

async def test_login():
    async with openmcp.browser() as browser:
        await browser.navigate("https://myapp.com/login")
        await browser.type("#email", "test@example.com")
        await browser.type("#password", "password123")
        await browser.click("#login-button")
        await browser.screenshot("login_result.png")
```

### **Claude Desktop Integration**
Tell Claude: *"Take screenshots of our top 5 product pages"*

Claude uses openmcp automatically:
```python
import openmcp

async def screenshot_products():
    products = ["product1", "product2", "product3", "product4", "product5"]
    
    async with openmcp.browser() as browser:
        for product in products:
            await browser.navigate(f"https://mystore.com/{product}")
            await browser.screenshot(f"{product}.png")
```

## 🔧 Available Methods

### **MCP Class**
```python
mcp = openmcp.MCP("browseruse")
await mcp.create_session()          # Create browser session
await mcp.health_check()            # Check server health
await mcp.list_tools()              # List available tools
await mcp.quick_screenshot(url)     # Quick screenshot
await mcp.quick_navigate(url)       # Quick navigation
```

### **BrowserSession Class**
```python
session = await mcp.create_session()
await session.navigate(url)         # Navigate to URL
await session.click(selector)       # Click element
await session.type(selector, text)  # Type text
await session.find(selector)        # Find elements
await session.screenshot(filename)  # Take screenshot
await session.page_info()           # Get page info
await session.close()               # Close session
```

### **Convenience Functions**
```python
await openmcp.screenshot(url, filename)     # One-liner screenshot
await openmcp.test_form(url, form_data)     # One-liner form test
await openmcp.ensure_server_running()      # Check server status

# Context manager
async with openmcp.browser() as browser:
    # Use browser here
    pass
```

## 🎉 Benefits

### ✅ **Developer Experience**
- **Intuitive**: Pythonic, object-oriented interface
- **Simple**: No HTTP requests or JSON handling
- **Safe**: Automatic resource cleanup
- **Smart**: Auto-detects API keys and configuration

### ✅ **AI Assistant Friendly**
- **Readable**: Clear method names and patterns
- **Predictable**: Consistent API across all operations
- **Documented**: Rich docstrings and examples
- **Extensible**: Easy to add new services

### ✅ **Production Ready**
- **Error Handling**: Proper exceptions with clear messages
- **Resource Management**: Automatic session cleanup
- **Configuration**: Flexible API key and server configuration
- **Async**: Full async/await support

## 🚀 Migration Guide

### From HTTP API
```python
# Old HTTP way
async with httpx.AsyncClient() as client:
    response = await client.post(url, headers=headers, json=payload)
    result = response.json()

# New simple way
mcp = openmcp.MCP("browseruse")
session = await mcp.create_session()
result = await session.navigate("https://example.com")
```

### From Complex MCP Protocol
```python
# Old MCP protocol way
from mcp.client.stdio import stdio_client
session = await stdio_client(server_params)
result = await session.call_tool("navigate", {"url": "https://example.com"})

# New simple way
async with openmcp.browser() as browser:
    await browser.navigate("https://example.com")
```

## 🎯 Use Cases

### **Web Testing**
```python
async def test_checkout_flow():
    async with openmcp.browser() as browser:
        await browser.navigate("https://shop.com")
        await browser.click("#add-to-cart")
        await browser.click("#checkout")
        await browser.type("#email", "test@example.com")
        await browser.screenshot("checkout.png")
```

### **Data Scraping**
```python
async def scrape_prices():
    async with openmcp.browser() as browser:
        await browser.navigate("https://shop.com/products")
        prices = await browser.find(".price")
        return [p["text"] for p in prices]
```

### **Form Automation**
```python
async def fill_contact_form():
    form_data = {
        "#name": "John Doe",
        "#email": "john@example.com",
        "#message": "Hello from openmcp!"
    }
    await openmcp.test_form("https://example.com/contact", form_data)
```

### **Visual Testing**
```python
async def visual_regression_test():
    pages = ["/", "/about", "/contact", "/products"]
    
    async with openmcp.browser() as browser:
        for page in pages:
            await browser.navigate(f"https://mysite.com{page}")
            await browser.screenshot(f"page_{page.replace('/', 'home')}.png")
```

## 🎉 Summary

The new simple interface transforms openmcp from a technical tool into an **intuitive, AI-friendly library** that anyone can use:

- **One line to get started**: `mcp = openmcp.MCP("browseruse")`
- **Context managers for safety**: `async with openmcp.browser():`
- **One-liners for quick tasks**: `await openmcp.screenshot(url)`
- **Perfect for AI assistants**: Clean, predictable patterns
- **Production ready**: Proper error handling and resource management

**🚀 Ready to use in your projects and perfect for Cursor/Claude to generate automatically!**
