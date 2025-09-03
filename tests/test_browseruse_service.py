"""Test cases for browseruse service."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from openmcp.services.browseruse_service import BrowseruseService, BrowserSession


class TestBrowserSession:
    """Test browser session functionality."""
    
    @pytest.fixture
    def browser_session(self):
        """Create test browser session."""
        return BrowserSession("test-session", headless=True, timeout=30)
    
    @pytest.mark.asyncio
    async def test_start_session(self, browser_session):
        """Test starting browser session."""
        with patch('selenium.webdriver.Chrome') as mock_driver:
            with patch('webdriver_manager.chrome.ChromeDriverManager') as mock_manager:
                mock_manager.return_value.install.return_value = "/path/to/chromedriver"
                mock_driver_instance = MagicMock()
                mock_driver.return_value = mock_driver_instance
                
                await browser_session.start()
                
                assert browser_session.is_active is True
                assert browser_session.driver is not None
                mock_driver.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stop_session(self, browser_session):
        """Test stopping browser session."""
        # Mock driver
        mock_driver = MagicMock()
        browser_session.driver = mock_driver
        browser_session.is_active = True
        
        await browser_session.stop()
        
        assert browser_session.is_active is False
        assert browser_session.driver is None
        mock_driver.quit.assert_called_once()
    
    def test_navigate(self, browser_session):
        """Test navigation."""
        mock_driver = MagicMock()
        mock_driver.current_url = "https://example.com"
        mock_driver.title = "Example Domain"
        browser_session.driver = mock_driver
        
        result = browser_session.navigate("https://example.com")
        
        assert result["url"] == "https://example.com"
        assert result["title"] == "Example Domain"
        assert result["status"] == "success"
        mock_driver.get.assert_called_once_with("https://example.com")
    
    def test_navigate_no_driver(self, browser_session):
        """Test navigation without driver should raise error."""
        with pytest.raises(RuntimeError) as exc_info:
            browser_session.navigate("https://example.com")
        
        assert "Browser session not started" in str(exc_info.value)
    
    def test_get_page_info(self, browser_session):
        """Test getting page info."""
        mock_driver = MagicMock()
        mock_driver.current_url = "https://example.com"
        mock_driver.title = "Example Domain"
        mock_driver.page_source = "<html><body>Test</body></html>"
        browser_session.driver = mock_driver
        
        info = browser_session.get_page_info()
        
        assert info["url"] == "https://example.com"
        assert info["title"] == "Example Domain"
        assert info["page_source_length"] == len("<html><body>Test</body></html>")
    
    def test_find_elements(self, browser_session):
        """Test finding elements."""
        mock_driver = MagicMock()
        mock_element1 = MagicMock()
        mock_element1.tag_name = "button"
        mock_element1.text = "Click me"
        mock_element1.get_attribute.side_effect = lambda attr: {
            "id": "btn1", "class": "button", "href": None
        }.get(attr)
        
        mock_element2 = MagicMock()
        mock_element2.tag_name = "a"
        mock_element2.text = "Link"
        mock_element2.get_attribute.side_effect = lambda attr: {
            "id": "link1", "class": "link", "href": "https://example.com"
        }.get(attr)
        
        mock_driver.find_elements.return_value = [mock_element1, mock_element2]
        browser_session.driver = mock_driver
        
        elements = browser_session.find_elements("button", "css")
        
        assert len(elements) == 2
        assert elements[0]["tag"] == "button"
        assert elements[0]["text"] == "Click me"
        assert elements[1]["tag"] == "a"
        assert elements[1]["text"] == "Link"
    
    def test_click_element(self, browser_session):
        """Test clicking element."""
        with patch('openmcp.services.browseruse_service.WebDriverWait') as mock_wait:
            with patch('openmcp.services.browseruse_service.EC'):
                mock_driver = MagicMock()
                mock_driver.current_url = "https://example.com/after-click"
                browser_session.driver = mock_driver
                
                mock_element = MagicMock()
                mock_wait.return_value.until.return_value = mock_element
                
                result = browser_session.click_element("#button", "css")
                
                assert result["status"] == "success"
                assert result["current_url"] == "https://example.com/after-click"
                mock_element.click.assert_called_once()
    
    def test_type_text(self, browser_session):
        """Test typing text."""
        with patch('openmcp.services.browseruse_service.WebDriverWait') as mock_wait:
            with patch('openmcp.services.browseruse_service.EC'):
                mock_driver = MagicMock()
                browser_session.driver = mock_driver
                
                mock_element = MagicMock()
                mock_wait.return_value.until.return_value = mock_element
                
                result = browser_session.type_text("#input", "test text", "css")
                
                assert result["status"] == "success"
                mock_element.clear.assert_called_once()
                mock_element.send_keys.assert_called_once_with("test text")
    
    def test_take_screenshot(self, browser_session):
        """Test taking screenshot."""
        mock_driver = MagicMock()
        mock_driver.get_screenshot_as_base64.return_value = "fake-base64-data"
        browser_session.driver = mock_driver
        
        result = browser_session.take_screenshot()
        
        assert result == "fake-base64-data"
        mock_driver.get_screenshot_as_base64.assert_called_once()


class TestBrowseruseService:
    """Test browseruse service."""
    
    @pytest.fixture
    def service(self):
        """Create test service."""
        config = {
            "headless": True,
            "timeout": 30,
            "max_sessions": 5
        }
        return BrowseruseService(config)
    
    @pytest.mark.asyncio
    async def test_start_service(self, service):
        """Test starting service."""
        await service.start()
        
        assert service.is_running is True
    
    @pytest.mark.asyncio
    async def test_stop_service(self, service):
        """Test stopping service."""
        # Add some mock sessions
        mock_session1 = AsyncMock()
        mock_session2 = AsyncMock()
        service.sessions = {
            "session1": mock_session1,
            "session2": mock_session2
        }
        
        await service.stop()
        
        assert service.is_running is False
        assert len(service.sessions) == 0
        mock_session1.stop.assert_called_once()
        mock_session2.stop.assert_called_once()
    
    def test_get_tools(self, service):
        """Test getting available tools."""
        tools = service.get_tools()
        
        assert len(tools) > 0
        
        tool_names = [tool["name"] for tool in tools]
        expected_tools = [
            "create_session", "navigate", "find_elements",
            "click_element", "type_text", "take_screenshot", "close_session"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    @pytest.mark.asyncio
    async def test_create_session_tool(self, service):
        """Test create_session tool."""
        with patch.object(service, '_create_session') as mock_create:
            mock_create.return_value = {
                "session_id": "test-session",
                "status": "created"
            }
            
            result = await service.call_tool(
                "create_session",
                {"headless": True, "timeout": 30}
            )
            
            assert result["session_id"] == "test-session"
            assert result["status"] == "created"
    
    @pytest.mark.asyncio
    async def test_navigate_tool(self, service):
        """Test navigate tool."""
        # Create mock session
        mock_session = MagicMock()
        mock_session.navigate.return_value = {
            "url": "https://example.com",
            "title": "Example",
            "status": "success"
        }
        service.sessions["test-session"] = mock_session
        
        result = await service.call_tool(
            "navigate",
            {"url": "https://example.com"},
            "test-session"
        )
        
        assert result["url"] == "https://example.com"
        assert result["title"] == "Example"
        mock_session.navigate.assert_called_once_with("https://example.com")
    
    @pytest.mark.asyncio
    async def test_tool_no_session(self, service):
        """Test tool call without session should return error."""
        result = await service.call_tool(
            "navigate",
            {"url": "https://example.com"},
            "nonexistent-session"
        )
        
        assert "error" in result
        assert "No active session" in result["error"]
    
    @pytest.mark.asyncio
    async def test_create_session_max_limit(self, service):
        """Test creating session when at max limit."""
        # Fill up to max sessions
        for i in range(service.max_sessions):
            service.sessions[f"session-{i}"] = MagicMock()
        
        result = await service._create_session({"headless": True})
        
        assert "error" in result
        assert "Maximum sessions" in result["error"]
    
    @pytest.mark.asyncio
    async def test_close_session_tool(self, service):
        """Test close_session tool."""
        # Create mock session
        mock_session = AsyncMock()
        service.sessions["test-session"] = mock_session
        
        result = await service._close_session("test-session")
        
        assert result["status"] == "closed"
        assert "test-session" not in service.sessions
        mock_session.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_nonexistent_session(self, service):
        """Test closing nonexistent session."""
        result = await service._close_session("nonexistent")
        
        assert "error" in result
        assert "Session not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_tool_exception_handling(self, service):
        """Test tool call exception handling."""
        # Mock session that raises exception
        mock_session = MagicMock()
        mock_session.navigate.side_effect = Exception("Test error")
        service.sessions["test-session"] = mock_session
        
        result = await service.call_tool(
            "navigate",
            {"url": "https://example.com"},
            "test-session"
        )
        
        assert "error" in result
        assert "Test error" in result["error"]
