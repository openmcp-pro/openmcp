# openmcp 🚀

<div align="center">

**The Ultimate MCP Server for AI Agents**  
*Supercharge your AI coding assistants with powerful web automation*

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-purple.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

## 🎯 What is openmcp?

**openmcp** is a production-ready MCP (Model Context Protocol) server that gives AI agents **superpowers** for web automation. Whether you're using **Cursor**, **Claude**, **ChatGPT**, or any other AI assistant, openmcp provides secure, scalable access to browser automation capabilities.

### 🌟 Perfect for AI-Powered Development

- **🔥 Cursor Integration** - Let Cursor automate web testing and scraping
- **🤖 Claude Desktop** - Give Claude the ability to browse and interact with websites  
- **💻 VS Code Extensions** - Power up your AI coding assistants
- **🔧 Custom AI Agents** - Build agents that can navigate the web
- **📊 Data Collection** - Automate web scraping and form filling
- **🧪 Testing Automation** - Let AI write and run web tests

## ✨ Key Features

<table>
<tr>
<td width="50%">

### 🔐 **Enterprise Ready**
- **API Key Authentication** - Secure access control
- **Localhost Development Mode** - No auth required from localhost
- **Mock API Key Support** - Easy testing with `openmcp-localhost-auth`
- **Permission Management** - Fine-grained service access
- **Rate Limiting** - Prevent abuse and overuse
- **Audit Logging** - Track all AI agent activities

</td>
<td width="50%">

### 🌐 **Universal Access**
- **HTTP REST API** - Works with any language/tool
- **Native MCP Protocol** - Direct MCP client support
- **Remote Access** - Agents connect from anywhere
- **Load Balancer Ready** - Scale horizontally

</td>
</tr>
<tr>
<td width="50%">

### 🔧 **Powerful Automation**
- **Browser Sessions** - Manage multiple browser instances
- **Element Interaction** - Click, type, scroll, navigate
- **Screenshot Capture** - Visual feedback for AI agents
- **Form Automation** - Fill and submit complex forms

</td>
<td width="50%">

### 🚀 **Developer Friendly**
- **5-Minute Setup** - Get running instantly
- **Docker Support** - Deploy anywhere
- **Rich Documentation** - Comprehensive guides
- **Multiple Examples** - Copy-paste ready code

</td>
</tr>
</table>

## 🚀 Quick Start (5 Minutes)

### 1. Install openmcp

```bash
# Clone and install
git clone https://github.com/openmcp/openmcp.git
cd openmcp
pip install -e .
```

### 2. Initialize and Start

```bash
# Create configuration and get your API key
openmcp init-config

# Start the server
openmcp serve
```

**🎉 That's it!** Your openmcp server is running on `http://localhost:9000`

### 3. Use the Super Simple Interface

```python
import asyncio
import openmcp

async def main():
    # Super simple - just one line!
    mcp = openmcp.MCP("browseruse")
    
    # Create a browser session
    session = await mcp.create_session()
    
    # Navigate and take screenshot
    await session.navigate("https://example.com")
    await session.screenshot("example.png")
    
    # Clean up
    await session.close()

# Or even simpler with context manager:
async def even_simpler():
    async with openmcp.browser() as browser:
        await browser.navigate("https://example.com")
        await browser.click("#some-button")
        await browser.screenshot("result.png")

# One-liner screenshot
async def one_liner():
    await openmcp.screenshot("https://example.com", "quick.png")

asyncio.run(main())
```

## 🔐 Authentication & Development Mode

openmcp supports multiple authentication modes to make development easy while keeping production secure:

### 🚀 Development Mode (Localhost)

**No API key required** when connecting from localhost! Perfect for development:

```python
# From localhost - no auth needed!
import httpx

async def localhost_example():
    # Direct API calls without authentication
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:9000/api/v1/services")
        print(response.json())

# Or with the simple interface
import openmcp
mcp = openmcp.MCP("browseruse")  # No API key needed from localhost!
```

### 🧪 Mock API Key for Testing

Use the built-in mock API key `openmcp-localhost-auth` for testing from any location:

```python
# Works from anywhere - great for CI/CD
import openmcp

# Using mock API key
mcp = openmcp.MCP("browseruse", api_key="openmcp-localhost-auth")

# Or direct HTTP with mock key
headers = {"Authorization": "Bearer openmcp-localhost-auth"}
```

### 🔒 Production API Keys

For production use, generate secure API keys:

```bash
# Generate production API key
openmcp init-config  # Shows your API key

# Use in production
export OPENMCP_API_KEY="bmcp_your-production-key-here"
```

### 🛠️ Configuration Options

Control authentication behavior in your config:

```yaml
# config.yaml
auth:
  allow_localhost: true           # Enable localhost bypass (default: true)
  mock_api_key: "openmcp-localhost-auth"  # Mock key for testing
  secret_key: "your-secret-key"   # JWT secret
```

### 🎯 Which Mode to Use?

- **🏠 Local Development**: No API key needed - just run and go!
- **🧪 Testing/CI**: Use `openmcp-localhost-auth` mock key
- **🚀 Production**: Generate and use secure `bmcp_` API keys
- **🔒 Restricted**: Disable localhost mode in production configs

## ⚡ Super Simple Interface

**NEW!** openmcp now has an incredibly simple Python interface:

```python
import openmcp

# Just one line to get started!
mcp = openmcp.MCP("browseruse")
```

### 🎯 Three Ways to Use openmcp

#### 1. **Session-based (Full Control)**
```python
mcp = openmcp.MCP("browseruse")
session = await mcp.create_session()
await session.navigate("https://example.com")
await session.click("#button")
await session.screenshot("result.png")
await session.close()
```

#### 2. **Context Manager (Recommended)**
```python
async with openmcp.browser() as browser:
    await browser.navigate("https://example.com")
    await browser.type("#search", "openmcp")
    await browser.click("#submit")
    await browser.screenshot("search_results.png")
# Automatically cleaned up!
```

#### 3. **One-Liners (Super Quick)**
```python
# Quick screenshot
await openmcp.screenshot("https://example.com", "page.png")

# Quick form test
await openmcp.test_form("https://example.com/contact", {
    "#name": "John Doe",
    "#email": "john@example.com"
})
```

### 🤖 Perfect for AI Assistants

**Ask Cursor or Claude:**
- *"Create a script using openmcp.browser() to test our login form"*
- *"Use openmcp to take screenshots of all our product pages"*
- *"Write a openmcp script that fills out contact forms automatically"*

They'll generate clean, simple code using the new interface!

## 🔥 Using openmcp with Cursor

### Method 1: Super Simple Interface (Recommended)

Just add this to your project and ask Cursor to use it:

```python
import openmcp

# Cursor will generate code like this:
async def test_website():
    async with openmcp.browser() as browser:
        await browser.navigate("https://yoursite.com")
        await browser.click("#login-button")
        await browser.type("#email", "test@example.com")
        await browser.screenshot("login_page.png")
```

### Method 2: Direct HTTP Integration

Add this to your Cursor project to give your AI assistant web automation powers:

```python
# cursor_openmcp.py - Add this to your project
import httpx
import asyncio
from typing import Dict, Any, Optional

class CursorWebAutomation:
    """Web automation helper for Cursor AI assistant."""
    
    def __init__(self, api_key: str = "", base_url: str = "http://localhost:9000"):
        self.api_key = api_key
        self.base_url = base_url
        # Only add auth header if API key is provided (localhost mode doesn't need it)
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self.session_id: Optional[str] = None
    
    async def start_browser(self, headless: bool = True) -> str:
        """Start a browser session for automation."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/browseruse/call",
                headers=self.headers,
                json={
                    "tool_name": "create_session",
                    "arguments": {"headless": headless, "timeout": 30}
                }
            )
            result = response.json()
            if result["success"]:
                self.session_id = result["result"]["session_id"]
                return self.session_id
            raise Exception(f"Failed to start browser: {result}")
    
    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL."""
        if not self.session_id:
            await self.start_browser()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/browseruse/call",
                headers=self.headers,
                json={
                    "tool_name": "navigate",
                    "arguments": {"url": url},
                    "session_id": self.session_id
                }
            )
            return response.json()
    
    async def find_and_click(self, selector: str) -> Dict[str, Any]:
        """Find and click an element."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/browseruse/call",
                headers=self.headers,
                json={
                    "tool_name": "click_element",
                    "arguments": {"selector": selector},
                    "session_id": self.session_id
                }
            )
            return response.json()
    
    async def type_text(self, selector: str, text: str) -> Dict[str, Any]:
        """Type text into an input field."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/browseruse/call",
                headers=self.headers,
                json={
                    "tool_name": "type_text",
                    "arguments": {"selector": selector, "text": text},
                    "session_id": self.session_id
                }
            )
            return response.json()
    
    async def screenshot(self, save_path: str = "screenshot.png") -> str:
        """Take a screenshot and save it."""
        async with httpx.AsyncClient() as client:
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
                import base64
                screenshot_data = base64.b64decode(result["result"]["screenshot"])
                with open(save_path, "wb") as f:
                    f.write(screenshot_data)
                return save_path
            raise Exception("Screenshot failed")

# Usage example for Cursor
async def demo_for_cursor():
    """Demo function that Cursor can call."""
    # No API key needed from localhost! For remote use: api_key="openmcp-localhost-auth"
    automation = CursorWebAutomation()  # Empty for localhost, or use mock key
    
    # Navigate to a website
    await automation.navigate("https://example.com")
    
    # Take a screenshot
    screenshot_path = await automation.screenshot("example_page.png")
    print(f"Screenshot saved: {screenshot_path}")
    
    # You can now ask Cursor to:
    # - Automate form filling
    # - Scrape website data  
    # - Test web applications
    # - Generate web automation scripts

# Run this in Cursor's terminal
if __name__ == "__main__":
    asyncio.run(demo_for_cursor())
```

### Method 2: MCP Integration (Advanced)

For native MCP support in Cursor, add this configuration:

```json
// .cursor/mcp_config.json
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

### 🎯 Cursor Use Cases

**Ask Cursor to:**
- *"Create a script that logs into this website and downloads all PDFs"*
- *"Write a test that fills out this contact form and verifies submission"*
- *"Build a scraper that extracts product prices from this e-commerce site"*
- *"Automate taking screenshots of our website on different screen sizes"*

## 🤖 Using openmcp with Claude Desktop

### Setup Claude Desktop Integration

1. **Install Claude Desktop** from Anthropic
2. **Configure MCP Server** in Claude's settings:

```json
// Claude Desktop MCP Configuration
{
  "mcpServers": {
    "openmcp-browser": {
      "command": "openmcp",
      "args": ["serve", "--protocol", "mcp"]
    }
  }
}
```

3. **Restart Claude Desktop** - openmcp tools will appear automatically

### 🎯 Claude Desktop Use Cases

**Ask Claude:**
- *"Please navigate to GitHub and take a screenshot of the trending repositories"*
- *"Fill out this job application form with my resume details"*
- *"Check if my website loads correctly and take screenshots"*
- *"Find all the contact forms on this website and test them"*

### Example Claude Conversation

```
You: "Please help me test the contact form on https://example.com"

Claude: I'll help you test the contact form. Let me:
1. Create a browser session
2. Navigate to the website  
3. Find the contact form
4. Fill it out with test data
5. Take screenshots of the process

[Claude automatically uses openmcp tools to complete the task]
```

## 🔧 Available Tools

| Tool | Description | Example Use Case |
|------|-------------|------------------|
| **create_session** | Start new browser | *"Start a browser for testing"* |
| **navigate** | Go to URL | *"Open the login page"* |
| **find_elements** | Locate page elements | *"Find all the buttons on this page"* |
| **click_element** | Click buttons/links | *"Click the submit button"* |
| **type_text** | Fill input fields | *"Enter my email address"* |
| **take_screenshot** | Capture page image | *"Take a screenshot for documentation"* |
| **close_session** | End browser session | *"Clean up when done"* |

## 📊 Real-World Examples

### Example 1: Automated Testing with Cursor

```python
# test_automation.py - Generated by Cursor with openmcp
import asyncio
from cursor_openmcp import CursorWebAutomation

async def test_login_flow():
    """Test user login functionality."""
    automation = CursorWebAutomation()  # No auth needed from localhost!
    
    # Navigate to login page
    await automation.navigate("https://yourapp.com/login")
    
    # Fill login form
    await automation.type_text("#email", "test@example.com")
    await automation.type_text("#password", "testpass123")
    
    # Submit form
    await automation.find_and_click("#login-button")
    
    # Verify success
    await asyncio.sleep(2)  # Wait for redirect
    screenshot = await automation.screenshot("login_success.png")
    
    print(f"Login test completed. Screenshot: {screenshot}")

# Cursor can generate and run this automatically!
asyncio.run(test_login_flow())
```

### Example 2: Data Collection with Claude

```
You: "Please collect all product names and prices from https://shop.example.com"

Claude: I'll help you scrape the product data. Let me:

1. Navigate to the shop website
2. Find all product elements  
3. Extract names and prices
4. Save the data to a CSV file

[Uses openmcp tools automatically]

Here's the collected data:
- Product A: $29.99
- Product B: $39.99
- Product C: $19.99

Data saved to products.csv
```

### Example 3: Form Automation

```python
# Generated by AI assistant using openmcp
async def automate_job_application():
    automation = CursorWebAutomation()  # Localhost = no auth required!
    
    # Navigate to job application
    await automation.navigate("https://company.com/careers/apply")
    
    # Fill personal information
    await automation.type_text("#first-name", "John")
    await automation.type_text("#last-name", "Doe")
    await automation.type_text("#email", "john@example.com")
    
    # Upload resume (if file upload is supported)
    await automation.find_and_click("#resume-upload")
    
    # Take screenshot for verification
    await automation.screenshot("application_filled.png")
    
    print("Job application automated successfully!")
```

## 🚀 Advanced Configuration

### Custom Service Configuration

```yaml
# config.yaml
server:
  host: "0.0.0.0"
  port: 9000
  debug: false

auth:
  secret_key: "your-secret-key"
  
services:
  - name: "browseruse"
    enabled: true
    config:
      headless: true
      timeout: 30
      max_sessions: 10  # Allow more concurrent sessions
      
  # Add more services here
  - name: "future_service"
    enabled: false
```

### Environment Variables

```bash
# .env
OPENMCP_SECRET_KEY=your-production-secret
OPENMCP_HOST=0.0.0.0
OPENMCP_PORT=9000
OPENMCP_MAX_SESSIONS=20
```

## 🐳 Production Deployment

### Docker Deployment

```bash
# Build and run
docker build -t openmcp .
docker run -p 9000:9000 -e OPENMCP_SECRET_KEY=your-secret openmcp
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  openmcp:
    build: .
    ports:
      - "9000:9000"
    environment:
      - OPENMCP_SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./config.yaml:/app/config.yaml
    restart: unless-stopped
```

### Cloud Deployment

**Deploy to any cloud platform:**
- **AWS ECS/Fargate** - Container-ready
- **Google Cloud Run** - Serverless scaling  
- **Azure Container Instances** - Easy deployment
- **DigitalOcean Apps** - Simple setup
- **Railway/Render** - One-click deploy

## 🔒 Security Best Practices

### API Key Management
```bash
# Generate secure API keys
openmcp create-key "production-agent" --expires 365

# Rotate keys regularly
openmcp create-key "new-key" --expires 90
# Update your applications
# Revoke old key
```

### Network Security
```yaml
# config.yaml - Production settings
server:
  host: "127.0.0.1"  # Only local access
  port: 9000

auth:
  allow_localhost: false  # Disable localhost bypass in production
  mock_api_key: ""        # Disable mock key in production

# Use reverse proxy (nginx/traefik) for HTTPS
# Enable firewall rules
# Use VPN for remote access
```

## 📈 Monitoring & Observability

### Health Checks
```bash
# Monitor server health
curl http://localhost:9000/health

# Check service status
curl -H "Authorization: Bearer $API_KEY" \
     http://localhost:9000/api/v1/services/browseruse/status
```

### Logging
```python
# Structured logging is built-in
import structlog
logger = structlog.get_logger()

# All API calls are automatically logged
# Browser actions are tracked
# Errors are captured with context
```

## 🪝 Git Hooks

This repository includes git hooks to maintain clean commit history:

### Claude Keyword Filter

Automatically removes lines containing "Claude" from commit messages to keep them professional:

```bash
# Input commit message:
"Add new feature
Claude helped with implementation  
Fix authentication bug"

# Automatically filtered to:
"Add new feature
Fix authentication bug"
```

**Features:**
- **🔍 Auto-Detection** - Finds "Claude" keyword (case-insensitive)
- **🧹 Smart Filtering** - Removes only problematic lines
- **🔄 Safe Fallback** - Never leaves empty commit messages
- **📝 Visual Feedback** - Shows what was filtered

See [GIT_HOOKS.md](GIT_HOOKS.md) for complete documentation.

## 🤝 Contributing & Extending

### Adding New Services

```python
# my_custom_service.py
from openmcp.services.base import BaseMCPService

class MyCustomService(BaseMCPService):
    def get_tools(self):
        return [{
            "name": "my_tool",
            "description": "My custom automation tool",
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {"type": "string"}
                }
            }
        }]
    
    async def call_tool(self, tool_name, arguments, session_id=None):
        if tool_name == "my_tool":
            # Implement your custom logic
            return {"result": f"Processed: {arguments['input']}"}
```

### Community Extensions

**Planned Services:**
- **📧 Email Automation** - Send/read emails
- **📱 Mobile Testing** - Appium integration  
- **🗄️ Database Operations** - SQL query execution
- **📊 API Testing** - REST/GraphQL testing
- **🔍 SEO Analysis** - Website optimization

## 🆘 Troubleshooting

### Common Issues

**Server won't start?**
```bash
# Check port availability
netstat -an | grep 9000

# Try different port
openmcp serve --port 8001
```

**Browser automation fails?**
```bash
# Install Chrome/Chromium
# Ubuntu/Debian:
sudo apt-get install chromium-browser

# macOS:
brew install --cask google-chrome

# Windows: Download from Google
```

**API authentication errors?**
```bash
# From localhost? No auth needed!
curl http://localhost:9000/api/v1/services

# Use mock key for testing
curl -H "Authorization: Bearer openmcp-localhost-auth" \
     http://localhost:9000/api/v1/services

# Regenerate API key for production
openmcp init-config --force

# Check key format (should start with 'bmcp_')
echo $API_KEY
```

**Cursor/Claude not connecting?**
```bash
# Verify MCP server starts
openmcp serve --protocol mcp

# Check MCP configuration syntax
# Restart Cursor/Claude Desktop
```

## 📚 Documentation & Resources

- **📖 [Complete API Documentation](http://localhost:9000/docs)** - Interactive OpenAPI docs
- **🎯 [MCP Examples Guide](MCP_EXAMPLES.md)** - Comprehensive usage examples  
- **⚡ [Quick Start Guide](QUICKSTART.md)** - 5-minute setup
- **🔧 [Configuration Reference](docs/configuration.md)** - All settings explained
- **🐛 [Troubleshooting Guide](docs/troubleshooting.md)** - Common issues & solutions

## 🌟 Community & Support

- **💬 [GitHub Discussions](https://github.com/openmcp/openmcp/discussions)** - Community Q&A
- **🐛 [Issue Tracker](https://github.com/openmcp/openmcp/issues)** - Bug reports & features
- **📧 [Email Support](mailto:support@openmcp.org)** - Direct help
- **🐦 [Twitter Updates](https://twitter.com/openmcp)** - Latest news

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with love using:
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[Selenium](https://selenium.dev/)** - Web browser automation
- **[Pydantic](https://pydantic.dev/)** - Data validation
- **[Typer](https://typer.tiangolo.com/)** - CLI interface
- **[Structlog](https://www.structlog.org/)** - Structured logging

---

<div align="center">

**🚀 Ready to supercharge your AI agents with web automation?**

[Get Started Now](#-quick-start-5-minutes) • [View Examples](examples/) • [Join Community](https://github.com/openmcp/openmcp/discussions)

Made with ❤️ for the AI development community

</div>