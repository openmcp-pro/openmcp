# openmcp MCP Service Examples 🔧

This document provides comprehensive examples of how to use the openmcp MCP service in different ways.

## 🎯 Overview

openmcp offers **two ways** to provide MCP services:

1. **HTTP API Server** (Default) - Universal access via REST API
2. **Native MCP Protocol** - Direct MCP protocol compliance

## 🌐 Method 1: HTTP API (Recommended)

### Start HTTP Server
```bash
# Default mode - HTTP API server
openmcp serve
# or explicitly
openmcp serve --protocol http
```

### Use with HTTP Client
```python
import httpx

class OpenMCPHTTPClient:
    def __init__(self, api_key: str):
        self.base_url = "http://localhost:8000"
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    async def create_browser_session(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/browseruse/call",
                headers=self.headers,
                json={
                    "tool_name": "create_session",
                    "arguments": {"headless": True}
                }
            )
            return response.json()

# Usage
client = OpenMCPHTTPClient("your-api-key")
session = await client.create_browser_session()
```

**Benefits:**
- ✅ Works with any programming language
- ✅ Universal HTTP protocol
- ✅ Built-in authentication
- ✅ Easy deployment and scaling
- ✅ Firewall-friendly

## 🔌 Method 2: Native MCP Protocol

### Start MCP Server
```bash
# Native MCP protocol server
openmcp serve --protocol mcp
```

### Use with MCP Client

#### Option A: Full MCP Client (Recommended)
```python
# examples/mcp_client_example.py
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class OpenMCPClient:
    def __init__(self, server_command: List[str]):
        self.server_command = server_command
        self.session: Optional[ClientSession] = None
    
    async def connect(self):
        server_params = StdioServerParameters(
            command=self.server_command[0],
            args=self.server_command[1:]
        )
        self.session = await stdio_client(server_params)
        await self.session.initialize()
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]):
        result = await self.session.call_tool(name, arguments)
        return json.loads(result.content[0].text)

# Usage
client = OpenMCPClient(["openmcp", "serve", "--protocol", "mcp"])
await client.connect()
result = await client.call_tool("create_browser_session", {"headless": True})
```

#### Option B: Simple JSON-RPC Client
```python
# examples/simple_mcp_example.py
import subprocess
import json

class SimpleMCPClient:
    def __init__(self, server_command: list):
        self.process = subprocess.Popen(
            server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
    
    async def call_tool(self, name: str, arguments: dict):
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments}
        }
        
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        
        response = json.loads(self.process.stdout.readline())
        return response["result"]

# Usage
client = SimpleMCPClient(["python", "-m", "openmcp.mcp_server"])
result = await client.call_tool("create_browser_session", {"headless": True})
```

**Benefits:**
- ✅ Native MCP protocol compliance
- ✅ Direct integration with MCP-aware clients
- ✅ Standardized tool discovery
- ✅ Efficient communication

## 🚀 Complete Examples

### Example 1: Web Search Automation

#### HTTP API Version
```bash
# Start server
openmcp init-config  # Get API key
openmcp serve

# Use the Python client
python examples/python_client.py
```

#### MCP Protocol Version
```bash
# Run MCP example
python examples/mcp_client_example.py
```

### Example 2: Form Interaction

Both examples include form interaction demos:
- Navigate to forms
- Fill input fields
- Select options
- Take screenshots
- Submit forms

## 🔧 Available Tools

All tools are available in both HTTP and MCP modes:

| Tool | Description | Parameters |
|------|-------------|------------|
| `create_browser_session` | Create new browser session | `headless`, `timeout` |
| `navigate` | Navigate to URL | `url`, `session_id` |
| `find_elements` | Find page elements | `selector`, `by`, `session_id` |
| `click_element` | Click an element | `selector`, `by`, `session_id` |
| `type_text` | Type text into element | `selector`, `text`, `by`, `session_id` |
| `take_screenshot` | Take page screenshot | `session_id` |
| `close_session` | Close browser session | `session_id` |

## 🎯 When to Use Which Method?

### Use HTTP API When:
- Building web applications
- Need remote access over internet
- Want maximum compatibility
- Require authentication/authorization
- Deploying behind load balancers
- Working with multiple programming languages

### Use Native MCP When:
- Building MCP-native applications
- Want direct protocol compliance
- Working with local/desktop agents
- Need efficient binary communication
- Integrating with MCP ecosystem tools

## 🔄 Running the Examples

### Prerequisites
```bash
# Install openmcp
pip install -e .

# Initialize configuration
openmcp init-config
```

### HTTP API Examples
```bash
# Basic HTTP client
python examples/python_client.py

# cURL examples
./examples/curl_examples.sh
```

### MCP Protocol Examples
```bash
# Full MCP client (requires mcp library)
pip install mcp
python examples/mcp_client_example.py

# Simple JSON-RPC client (no extra dependencies)
python examples/simple_mcp_example.py
```

## 🐛 Troubleshooting

### Common Issues

**Server won't start:**
```bash
# Check if port is available
netstat -an | grep 8000

# Try different port
openmcp serve --port 8001
```

**MCP connection fails:**
```bash
# Check server command
openmcp serve --protocol mcp --help

# Verify MCP library installation
pip install mcp
```

**Browser automation fails:**
```bash
# Install Chrome/Chromium
sudo apt-get install chromium-browser

# Check webdriver
python -c "from selenium import webdriver; print('OK')"
```

## 📚 Additional Resources

- **API Documentation**: Visit `http://localhost:8000/docs` when HTTP server is running
- **MCP Specification**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **Selenium Documentation**: [Selenium WebDriver](https://selenium-python.readthedocs.io/)

## 🎉 Next Steps

1. **Try the examples** - Run both HTTP and MCP examples
2. **Build your own client** - Use the patterns shown above
3. **Extend functionality** - Add new tools to the browseruse service
4. **Deploy in production** - Use Docker for easy deployment

The openmcp project provides flexible options for accessing powerful web automation capabilities through both standard HTTP APIs and native MCP protocol! 🚀
