# openmcp Quick Start Guide 🚀

## What is openmcp?

openmcp is a centralized server that provides optimized MCP (Model Context Protocol) services for AI agents. It allows agents from anywhere to connect remotely using API keys and access powerful capabilities like web browsing automation.

## 🎯 Key Features

- **🔐 Secure API Key Authentication** - Control access with generated API keys
- **🌐 Remote Access** - Agents can connect from anywhere via HTTP API
- **🔧 Modular Services** - Currently includes browseruse service for web automation
- **📊 RESTful API** - Standard HTTP API with comprehensive documentation
- **🐳 Docker Ready** - Easy deployment with Docker support

## ⚡ Quick Start (5 minutes)

### 1. Install openmcp

```bash
# Clone and install
git clone <your-repo-url>
cd openmcp
pip install -e .
```

### 2. Initialize Configuration

```bash
openmcp init-config
```

This creates a `config.yaml` file and shows your default API key:
```
Default API Key:
Name: default
Key: bmcp_lak0w6BVvPl2FFqhcAwyshdKnBsEUmJBLMHW3N6jiuw
```

**⚠️ Save this API key - you'll need it to connect!**

### 3. Start the Server

```bash
openmcp serve
```

The server starts on `http://localhost:8000`

### 4. Test with curl

```bash
# Check health
curl http://localhost:8000/health

# List services (replace YOUR_API_KEY)
curl -H "Authorization: Bearer YOUR_API_KEY" \
     http://localhost:8000/api/v1/services
```

## 🌐 Browser Automation Example

### Create a Browser Session

```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"tool_name": "create_session", "arguments": {"headless": true}}' \
     http://localhost:8000/api/v1/services/browseruse/call
```

Response:
```json
{
  "success": true,
  "result": {
    "session_id": "abc123...",
    "status": "created"
  }
}
```

### Navigate to a Website

```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"tool_name": "navigate", "arguments": {"url": "https://example.com"}, "session_id": "YOUR_SESSION_ID"}' \
     http://localhost:8000/api/v1/services/browseruse/call
```

### Take a Screenshot

```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"tool_name": "take_screenshot", "arguments": {}, "session_id": "YOUR_SESSION_ID"}' \
     http://localhost:8000/api/v1/services/browseruse/call
```

## 🐍 Python Client Example

```python
import asyncio
import httpx

class OpenMCPClient:
    def __init__(self, api_key: str):
        self.base_url = "http://localhost:8000"
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    async def create_browser_session(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/browseruse/call",
                headers=self.headers,
                json={"tool_name": "create_session", "arguments": {"headless": True}}
            )
            return response.json()

# Usage
async def main():
    client = OpenMCPClient("YOUR_API_KEY")
    session = await client.create_browser_session()
    print(f"Session created: {session['result']['session_id']}")

asyncio.run(main())
```

## 🔧 Available Tools

### Browseruse Service Tools:

- **create_session** - Create a new browser session
- **navigate** - Navigate to a URL
- **find_elements** - Find elements on the page
- **click_element** - Click an element
- **type_text** - Type text into an element
- **take_screenshot** - Take a screenshot
- **get_page_info** - Get current page information
- **close_session** - Close a browser session

## 📚 More Examples

Check out the `examples/` directory:
- `python_client.py` - Complete Python client with examples
- `curl_examples.sh` - Shell script with curl examples

## 🐳 Docker Deployment

```bash
# Build and run with Docker
docker build -t openmcp .
docker run -p 8000:8000 openmcp

# Or use docker-compose
docker-compose up
```

## 🔑 API Key Management

```bash
# Create additional API keys
openmcp create-key "my-agent" --expires 365

# List API keys via API
curl -H "Authorization: Bearer YOUR_API_KEY" \
     http://localhost:8000/api/v1/auth/keys
```

## 📖 Full Documentation

- **API Docs**: Visit `http://localhost:8000/docs` when server is running
- **README**: See `README.md` for complete documentation
- **Configuration**: Edit `config.yaml` to customize settings

## 🆘 Troubleshooting

### Server won't start?
- Check if port 8000 is available
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Browser automation not working?
- Install Chrome/Chromium browser
- For headless mode, ensure system supports it

### API calls failing?
- Verify API key is correct
- Check server logs for errors
- Ensure proper JSON formatting in requests

## 🎉 You're Ready!

Your openmcp server is now running and ready to serve AI agents with powerful web automation capabilities. Start building amazing AI applications! 

For more advanced usage, check out the full README.md and explore the examples directory.
