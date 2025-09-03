"""Test cases for the simple client interface."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile
from pathlib import Path

from openmcp.client import MCP, MCPClient, BrowserSession, MCPError


class TestMCPClient:
    """Test the simple MCP client."""
    
    @pytest.fixture
    def mock_httpx_response(self):
        """Create mock httpx response."""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "success": True,
            "result": {"session_id": "test-session-123"}
        }
        return response
    
    @pytest.fixture
    def client(self):
        """Create test client with mock API key."""
        with patch.object(MCPClient, '_auto_detect_api_key', return_value="test-api-key"):
            return MCPClient("browseruse", api_key="test-api-key")
    
    def test_client_creation(self):
        """Test client creation with API key."""
        client = MCPClient("browseruse", api_key="test-key")
        
        assert client.service_name == "browseruse"
        assert client.base_url == "http://localhost:9000"
        assert client.headers["Authorization"] == "Bearer test-key"
    
    def test_client_creation_no_api_key(self):
        """Test client creation without API key should raise error."""
        with patch.object(MCPClient, '_auto_detect_api_key', return_value=None):
            with pytest.raises(MCPError) as exc_info:
                MCPClient("browseruse")
            
            assert "No API key provided" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_call_tool_success(self, client, mock_httpx_response):
        """Test successful tool call."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_httpx_response
            
            result = await client._call_tool("test_tool", {"param": "value"})
            
            assert result["success"] is True
            assert result["result"]["session_id"] == "test-session-123"
    
    @pytest.mark.asyncio
    async def test_call_tool_http_error(self, client):
        """Test tool call with HTTP error."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            with pytest.raises(MCPError) as exc_info:
                await client._call_tool("test_tool", {})
            
            assert "HTTP 401" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_session(self, client, mock_httpx_response):
        """Test browser session creation."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_httpx_response
            
            session = await client.create_session()
            
            assert isinstance(session, BrowserSession)
            assert session.session_id == "test-session-123"
            assert session.client == client
    
    @pytest.mark.asyncio
    async def test_create_session_failure(self, client):
        """Test browser session creation failure."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "success": False,
                "error": "Failed to create session"
            }
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            with pytest.raises(MCPError) as exc_info:
                await client.create_session()
            
            assert "Failed to create session" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await client.health_check()
            
            assert result["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_list_tools(self, client):
        """Test listing tools."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "tools": [
                    {"name": "navigate", "description": "Navigate to URL"},
                    {"name": "click", "description": "Click element"}
                ]
            }
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            tools = await client.list_tools()
            
            assert len(tools) == 2
            assert tools[0]["name"] == "navigate"
            assert tools[1]["name"] == "click"


class TestBrowserSession:
    """Test browser session functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock client."""
        client = MagicMock()
        client._call_tool = AsyncMock()
        return client
    
    @pytest.fixture
    def session(self, mock_client):
        """Create test session."""
        return BrowserSession(mock_client, "test-session-123")
    
    @pytest.mark.asyncio
    async def test_navigate_success(self, session, mock_client):
        """Test successful navigation."""
        mock_client._call_tool.return_value = {
            "success": True,
            "result": {"url": "https://example.com", "title": "Example"}
        }
        
        result = await session.navigate("https://example.com")
        
        assert result["url"] == "https://example.com"
        assert result["title"] == "Example"
        
        mock_client._call_tool.assert_called_once_with("navigate", {
            "url": "https://example.com",
            "session_id": "test-session-123"
        })
    
    @pytest.mark.asyncio
    async def test_navigate_failure(self, session, mock_client):
        """Test navigation failure."""
        mock_client._call_tool.return_value = {
            "success": False,
            "error": "Navigation failed"
        }
        
        with pytest.raises(MCPError) as exc_info:
            await session.navigate("https://example.com")
        
        assert "Navigation failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_click_success(self, session, mock_client):
        """Test successful click."""
        mock_client._call_tool.return_value = {
            "success": True,
            "result": {"status": "clicked"}
        }
        
        result = await session.click("#button")
        
        assert result["status"] == "clicked"
        
        mock_client._call_tool.assert_called_once_with("click_element", {
            "selector": "#button",
            "by": "css",
            "session_id": "test-session-123"
        })
    
    @pytest.mark.asyncio
    async def test_type_success(self, session, mock_client):
        """Test successful text typing."""
        mock_client._call_tool.return_value = {
            "success": True,
            "result": {"status": "typed"}
        }
        
        result = await session.type("#input", "test text")
        
        assert result["status"] == "typed"
        
        mock_client._call_tool.assert_called_once_with("type_text", {
            "selector": "#input",
            "text": "test text",
            "by": "css",
            "session_id": "test-session-123"
        })
    
    @pytest.mark.asyncio
    async def test_find_elements(self, session, mock_client):
        """Test finding elements."""
        mock_client._call_tool.return_value = {
            "success": True,
            "result": {
                "elements": [
                    {"tag": "button", "text": "Click me"},
                    {"tag": "button", "text": "Submit"}
                ]
            }
        }
        
        elements = await session.find("button")
        
        assert len(elements) == 2
        assert elements[0]["text"] == "Click me"
        assert elements[1]["text"] == "Submit"
    
    @pytest.mark.asyncio
    async def test_screenshot(self, session, mock_client):
        """Test taking screenshot."""
        import base64
        
        # Create fake image data
        fake_image = b"fake-image-data"
        fake_b64 = base64.b64encode(fake_image).decode()
        
        mock_client._call_tool.return_value = {
            "success": True,
            "result": {"screenshot": fake_b64}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Take screenshot
            filepath = await session.screenshot("test.png", save_dir=str(temp_path))
            
            # Verify file was created
            assert Path(filepath).exists()
            
            # Verify file contents
            with open(filepath, "rb") as f:
                saved_data = f.read()
            
            assert saved_data == fake_image
    
    @pytest.mark.asyncio
    async def test_close_session(self, session, mock_client):
        """Test closing session."""
        mock_client._call_tool.return_value = {
            "success": True,
            "result": {"status": "closed"}
        }
        
        await session.close()
        
        assert session._closed is True
        
        mock_client._call_tool.assert_called_once_with("close_session", {
            "session_id": "test-session-123"
        })
    
    @pytest.mark.asyncio
    async def test_closed_session_operations(self, session):
        """Test operations on closed session should fail."""
        session._closed = True
        
        with pytest.raises(MCPError) as exc_info:
            await session.navigate("https://example.com")
        
        assert "Session is closed" in str(exc_info.value)


class TestMCP:
    """Test the main MCP interface."""
    
    @pytest.fixture
    def mcp(self):
        """Create test MCP instance."""
        with patch.object(MCPClient, '_auto_detect_api_key', return_value="test-api-key"):
            return MCP("browseruse", api_key="test-api-key")
    
    @pytest.mark.asyncio
    async def test_create_session(self, mcp):
        """Test session creation through MCP interface."""
        with patch.object(mcp.client, 'create_session') as mock_create:
            mock_session = MagicMock()
            mock_create.return_value = mock_session
            
            session = await mcp.create_session()
            
            assert session == mock_session
            mock_create.assert_called_once_with(True, 30)
    
    @pytest.mark.asyncio
    async def test_quick_screenshot(self, mcp):
        """Test quick screenshot functionality."""
        with patch.object(mcp, 'create_session') as mock_create:
            mock_session = AsyncMock()
            mock_session.navigate = AsyncMock()
            mock_session.screenshot = AsyncMock(return_value="screenshot.png")
            mock_session.close = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            
            mock_create.return_value = mock_session
            
            result = await mcp.quick_screenshot("https://example.com", "test.png")
            
            assert result == "screenshot.png"
            mock_session.navigate.assert_called_once_with("https://example.com")
            mock_session.screenshot.assert_called_once_with("test.png")
