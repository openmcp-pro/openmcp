# OpenMCP Transport Guide

## 🚀 Quick Command Reference

OpenMCP supports multiple transport protocols via the unified `openmcp serve` command:

```bash
# 🎯 Default: Official MCP with streamable-http transport (recommended)
openmcp serve

# ⚡ Official MCP with SSE transport (real-time streaming)
openmcp serve --transport sse

# 🔧 Legacy REST API transport (custom integrations)
openmcp serve --transport rest --port 9000
```

## 📊 Transport Comparison

| Transport | Protocol | Port | Best For | Client Support |
|-----------|----------|------|----------|----------------|
| **streamable-http** | MCP/HTTP | 8000 | Production, official clients | Official MCP clients |
| **sse** | MCP/SSE | 8000 | Real-time, streaming | Official MCP clients |
| **rest** | HTTP REST | 9000* | Custom integrations | Any HTTP client |

\* Port is configurable with `--port` option for REST transport

## 🎯 When to Use Each Transport

### **Streamable-HTTP (Default)**
- ✅ New projects using official MCP clients
- ✅ Production deployments
- ✅ Cursor, Claude Desktop, and other MCP-compatible tools
- ✅ Load balancer environments

### **SSE (Server-Sent Events)**
- ✅ Real-time progress monitoring
- ✅ Web dashboards with live updates
- ✅ Development and debugging
- ✅ Long-running operations with progress feedback

### **REST API (Legacy)**
- ✅ Existing applications with HTTP integrations
- ✅ Custom clients in any programming language
- ✅ Quick prototyping with curl/httpx
- ✅ Non-MCP environments

## 🔌 Client Connection Examples

### **Official MCP Client (streamable-http)**
```python
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession

async with streamablehttp_client('http://localhost:8000/') as (read_stream, write_stream, session_id):
    session = ClientSession(read_stream, write_stream)
    async with session:
        await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool('create_session', {'headless': True})
```

### **Official MCP Client (SSE)**
```python
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

async with sse_client('http://localhost:8000/sse') as (read_stream, write_stream):
    session = ClientSession(read_stream, write_stream)
    async with session:
        await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool('create_session', {'headless': True})
```

### **REST API Client**
```python
import httpx

async with httpx.AsyncClient() as client:
    # List services
    response = await client.get("http://localhost:9000/api/v1/services")
    services = response.json()
    
    # Create browser session
    response = await client.post(
        "http://localhost:9000/api/v1/services/browseruse/call",
        json={"tool_name": "create_session", "arguments": {"headless": True}}
    )
    result = response.json()
```

## 🛠️ Configuration Examples

### **MCP Client Configuration (Cursor)**
```json
// .cursor/mcp_config.json
{
  "mcpServers": {
    "openmcp": {
      "command": "openmcp",
      "args": ["serve", "--transport", "sse"],
      "env": {}
    }
  }
}
```

### **MCP Client Configuration (Claude Desktop)**
```json
// Claude Desktop MCP Configuration
{
  "mcpServers": {
    "openmcp-browser": {
      "command": "openmcp",
      "args": ["serve", "--transport", "sse"]
    }
  }
}
```

### **Docker Deployment**
```yaml
# docker-compose.yml
version: '3.8'
services:
  openmcp-mcp:
    build: .
    command: ["openmcp", "serve", "--transport", "streamable-http"]
    ports:
      - "8000:8000"
    environment:
      - OPENMCP_SECRET_KEY=${SECRET_KEY}

  openmcp-rest:
    build: .
    command: ["openmcp", "serve", "--transport", "rest", "--port", "9000"]
    ports:
      - "9000:9000"
    environment:
      - OPENMCP_SECRET_KEY=${SECRET_KEY}
```

## 🚀 Migration Guide

### **From Legacy HTTP to MCP**
```bash
# Old approach
openmcp serve --port 9000  # Legacy command (deprecated)

# New approach
openmcp serve --transport rest --port 9000  # Explicit REST transport
openmcp serve                                # Recommended: MCP streamable-http
```

### **From Custom API to Official MCP**
```python
# Old: Custom HTTP API
import httpx
client = httpx.AsyncClient()
response = await client.post("http://localhost:9000/api/v1/services/browseruse/call", ...)

# New: Official MCP Protocol
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession

async with streamablehttp_client('http://localhost:8000/') as streams:
    session = ClientSession(*streams[:2])
    result = await session.call_tool('create_session', {...})
```

## 💡 Tips & Best Practices

1. **🎯 Default Choice**: Use `openmcp serve` (streamable-http) for new projects
2. **⚡ Real-time Needs**: Use `--transport sse` for live progress monitoring
3. **🔧 Legacy Support**: Use `--transport rest` for existing HTTP integrations
4. **🔒 Production**: All transports support the same authentication and security features
5. **📊 Monitoring**: SSE transport provides the best visibility for debugging
6. **🚀 Performance**: Streamable-HTTP transport is optimized for production workloads

## 🆘 Troubleshooting

### **Port Conflicts**
```bash
# Check what's using port 8000
netstat -an | grep 8000

# Use different port for REST transport
openmcp serve --transport rest --port 8001
```

### **MCP Client Connection Issues**
```bash
# Test MCP server is running
curl http://localhost:8000/

# Verify correct transport
openmcp serve --transport sse  # For SSE clients
openmcp serve                  # For streamable-http clients
```

### **REST API Not Available**
```bash
# Ensure using REST transport
openmcp serve --transport rest --port 9000

# Test REST endpoint
curl http://localhost:9000/api/v1/services
```

---

**For more detailed information, see the main [README.md](README.md) and [examples/](examples/) directory.**