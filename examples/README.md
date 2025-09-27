# OpenMCP Examples

This directory contains examples showing different ways to integrate with OpenMCP.

## Available Examples

### 🎯 **Official MCP Examples** (Recommended)
Uses the official `mcp` Python library with OpenMCP's FastMCP server:

- **`simple_sse_demo.py`** - Clean MCP client with SSE streaming (works with `openmcp serve --transport sse`)
- **`mcp_client_sse.py`** - Full-featured official MCP client (works with `openmcp serve --transport sse`)

### 🌐 **Legacy HTTP API Examples**
Direct HTTP integration with OpenMCP's REST transport:

- **`simple_http_client.py`** - Basic HTTP API usage (works with `openmcp serve --transport rest`)
- **`sse_streaming_raw_demo.py`** - Raw SSE streaming (works with `openmcp serve --transport rest`)

### 🔀 **Comparison Examples**
Shows different integration approaches:

- **`comprehensive_demo.py`** - Compares HTTP, SSE, and Python client approaches

## Key Features

✅ **Localhost Authentication Bypass** - No API key needed from localhost  
✅ **Real-time Progress Updates** - SSE streaming for live feedback  
✅ **MCP Library Integration** - Official `mcp` Python library support  
✅ **Multiple Transport Options** - HTTP, SSE, and MCP client patterns  

## Quick Start

### 🎯 **For Official MCP Examples** (Recommended)

1. **Start OpenMCP FastMCP server with SSE:**
   ```bash
   openmcp serve --transport sse
   ```

2. **Run MCP examples:**
   ```bash
   python examples/simple_sse_demo.py        # Clean MCP + SSE
   python examples/mcp_client_sse.py         # Full MCP client
   ```

### 🌐 **For Legacy HTTP Examples**

1. **Start OpenMCP REST server:**
   ```bash
   openmcp serve --transport rest --port 9000
   ```

2. **Run HTTP examples:**
   ```bash
   python examples/simple_http_client.py     # Simple HTTP
   python examples/comprehensive_demo.py     # All approaches
   ```

### 🔄 **Mixed Approach Demo**

1. **Start any server:**
   ```bash
   openmcp serve  # Default: streamable-http transport
   ```

2. **Run comparison:**
   ```bash
   python examples/comprehensive_demo.py     # Tests multiple transports
   ```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │    │   HTTP Client    │    │  SSE Client     │
│                 │    │                  │    │                 │
│ Official MCP    │    │ Direct HTTP      │    │ Server-Sent     │
│ Library Types   │    │ API Calls        │    │ Events Stream   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    OpenMCP Server       │
                    │                         │
                    │  • Localhost Auth       │
                    │  • SSE Streaming        │
                    │  • Browser Automation   │
                    └─────────────────────────┘
```

## Recommendations

- 🎯 **For AI Agents**: Use `mcp_client_sse.py` (MCP + SSE)
- ⚡ **For Quick Scripts**: Use `simple_http_client.py` (HTTP)
- 📊 **For Dashboards**: Use SSE streaming approaches
- 🔄 **For Learning**: Run `comprehensive_demo.py` to see all approaches