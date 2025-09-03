"""Test cases for MCP service registry."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from openmcp.core.mcp_registry import MCPRegistry
from openmcp.services.base import BaseMCPService


class MockMCPService(BaseMCPService):
    """Mock MCP service for testing."""
    
    def __init__(self, config):
        super().__init__(config)
        self.started = False
        self.stopped = False
    
    async def start(self):
        """Mock start method."""
        self.started = True
        self.is_running = True
    
    async def stop(self):
        """Mock stop method."""
        self.stopped = True
        self.is_running = False
    
    def get_tools(self):
        """Mock get_tools method."""
        return [
            {
                "name": "mock_tool",
                "description": "A mock tool for testing",
                "parameters": {"type": "object"}
            }
        ]
    
    async def call_tool(self, tool_name, arguments, session_id=None):
        """Mock call_tool method."""
        if tool_name == "mock_tool":
            return {"result": "mock_result", "arguments": arguments}
        return {"error": f"Unknown tool: {tool_name}"}


class TestMCPRegistry:
    """Test MCP service registry."""
    
    @pytest.fixture
    def registry(self):
        """Create test registry."""
        return MCPRegistry()
    
    def test_register_service_class(self, registry):
        """Test service class registration."""
        registry.register_service_class("mock_service", MockMCPService)
        
        assert "mock_service" in registry.service_classes
        assert registry.service_classes["mock_service"] == MockMCPService
    
    @pytest.mark.asyncio
    async def test_start_service(self, registry):
        """Test starting a service."""
        registry.register_service_class("mock_service", MockMCPService)
        
        config = {"param1": "value1"}
        success = await registry.start_service("mock_service", config)
        
        assert success is True
        assert "mock_service" in registry.services
        
        service = registry.services["mock_service"]
        assert isinstance(service, MockMCPService)
        assert service.started is True
        assert service.is_running is True
    
    @pytest.mark.asyncio
    async def test_start_unregistered_service(self, registry):
        """Test starting an unregistered service."""
        success = await registry.start_service("nonexistent", {})
        assert success is False
    
    @pytest.mark.asyncio
    async def test_stop_service(self, registry):
        """Test stopping a service."""
        registry.register_service_class("mock_service", MockMCPService)
        
        # Start service first
        await registry.start_service("mock_service", {})
        assert "mock_service" in registry.services
        
        # Stop service
        success = await registry.stop_service("mock_service")
        
        assert success is True
        assert "mock_service" not in registry.services
    
    @pytest.mark.asyncio
    async def test_stop_nonexistent_service(self, registry):
        """Test stopping a non-running service."""
        success = await registry.stop_service("nonexistent")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_restart_service(self, registry):
        """Test restarting a service."""
        registry.register_service_class("mock_service", MockMCPService)
        
        # Start service first
        await registry.start_service("mock_service", {"param": "old"})
        old_service = registry.services["mock_service"]
        
        # Restart with new config
        success = await registry.restart_service("mock_service", {"param": "new"})
        
        assert success is True
        assert "mock_service" in registry.services
        
        new_service = registry.services["mock_service"]
        assert new_service is not old_service  # Should be new instance
        assert new_service.config["param"] == "new"
    
    def test_get_service(self, registry):
        """Test getting a service instance."""
        registry.register_service_class("mock_service", MockMCPService)
        
        # Should return None for non-running service
        service = registry.get_service("mock_service")
        assert service is None
        
        # Should return None for nonexistent service
        service = registry.get_service("nonexistent")
        assert service is None
    
    @pytest.mark.asyncio
    async def test_get_running_service(self, registry):
        """Test getting a running service instance."""
        registry.register_service_class("mock_service", MockMCPService)
        
        # Start service
        await registry.start_service("mock_service", {})
        
        # Should return service instance
        service = registry.get_service("mock_service")
        assert service is not None
        assert isinstance(service, MockMCPService)
    
    def test_list_services(self, registry):
        """Test listing running services."""
        registry.register_service_class("service1", MockMCPService)
        registry.register_service_class("service2", MockMCPService)
        
        # Initially no running services
        services = registry.list_services()
        assert len(services) == 0
    
    @pytest.mark.asyncio
    async def test_list_running_services(self, registry):
        """Test listing running services."""
        registry.register_service_class("service1", MockMCPService)
        registry.register_service_class("service2", MockMCPService)
        
        # Start one service
        await registry.start_service("service1", {})
        
        services = registry.list_services()
        assert len(services) == 1
        assert "service1" in services
    
    def test_list_available_services(self, registry):
        """Test listing available service classes."""
        registry.register_service_class("service1", MockMCPService)
        registry.register_service_class("service2", MockMCPService)
        
        available = registry.list_available_services()
        assert len(available) == 2
        assert "service1" in available
        assert "service2" in available
    
    @pytest.mark.asyncio
    async def test_stop_all_services(self, registry):
        """Test stopping all services."""
        registry.register_service_class("service1", MockMCPService)
        registry.register_service_class("service2", MockMCPService)
        
        # Start multiple services
        await registry.start_service("service1", {})
        await registry.start_service("service2", {})
        
        assert len(registry.list_services()) == 2
        
        # Stop all services
        await registry.stop_all_services()
        
        assert len(registry.list_services()) == 0
    
    def test_get_service_status(self, registry):
        """Test getting service status."""
        registry.register_service_class("mock_service", MockMCPService)
        
        # Status for non-running but available service
        status = registry.get_service_status("mock_service")
        assert status["status"] == "stopped"
        assert status["available"] is True
        
        # Status for nonexistent service
        status = registry.get_service_status("nonexistent")
        assert status["status"] == "stopped"
        assert status["available"] is False
    
    @pytest.mark.asyncio
    async def test_get_running_service_status(self, registry):
        """Test getting running service status."""
        registry.register_service_class("mock_service", MockMCPService)
        
        # Start service
        await registry.start_service("mock_service", {})
        
        # Status for running service
        status = registry.get_service_status("mock_service")
        assert status["status"] == "running"
        assert status["available"] is True
        assert status["health"] == "healthy"  # MockMCPService returns "healthy"
