"""Basic integration tests for openmcp."""

import pytest
from fastapi.testclient import TestClient

from openmcp.core.config import Config
from openmcp.core.server import OpenMCPServer


@pytest.fixture
def test_config():
    """Create test configuration."""
    return Config.create_default()


@pytest.fixture
def test_server(test_config):
    """Create test server."""
    return OpenMCPServer()


@pytest.fixture
def test_client(test_server):
    """Create test client."""
    app = test_server.create_app()
    return TestClient(app)


@pytest.fixture
def api_key(test_server):
    """Get a valid API key for testing."""
    api_keys = test_server.auth_manager.list_api_keys()
    return list(api_keys.keys())[0]


class TestBasicEndpoints:
    """Test basic server endpoints."""
    
    def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
    
    def test_root_endpoint(self, test_client):
        """Test root endpoint."""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "available_services" in data
        assert "running_services" in data


class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_list_services_without_auth(self, test_client):
        """Test accessing protected endpoint without auth."""
        response = test_client.get("/api/v1/services")
        assert response.status_code == 401
    
    def test_list_services_with_auth(self, test_client, api_key):
        """Test accessing protected endpoint with valid auth."""
        headers = {"Authorization": f"Bearer {api_key}"}
        response = test_client.get("/api/v1/services", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "available_services" in data
        assert "running_services" in data
        assert "service_details" in data
    
    def test_invalid_api_key(self, test_client):
        """Test invalid API key."""
        headers = {"Authorization": "Bearer invalid-key"}
        response = test_client.get("/api/v1/services", headers=headers)
        assert response.status_code == 401


class TestServiceEndpoints:
    """Test service-related endpoints."""
    
    def test_list_browseruse_tools(self, test_client, api_key):
        """Test listing browseruse tools."""
        headers = {"Authorization": f"Bearer {api_key}"}
        response = test_client.get(
            "/api/v1/services/browseruse/tools",
            headers=headers
        )
        # Service is not running, so it should return 404
        assert response.status_code == 404
    
    def test_browseruse_status(self, test_client, api_key):
        """Test browseruse service status."""
        headers = {"Authorization": f"Bearer {api_key}"}
        response = test_client.get(
            "/api/v1/services/browseruse/status",
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "available" in data
    
    def test_nonexistent_service(self, test_client, api_key):
        """Test accessing nonexistent service."""
        headers = {"Authorization": f"Bearer {api_key}"}
        response = test_client.get(
            "/api/v1/services/nonexistent/tools",
            headers=headers
        )
        # Should return 403 because permission check fails first
        assert response.status_code == 403


class TestIntegration:
    """Integration tests."""
    
    def test_config_creation(self):
        """Test configuration creation."""
        config = Config.create_default()
        assert config.server.host == "0.0.0.0"
        assert config.server.port == 9000
        assert config.auth.secret_key is not None
        assert len(config.services) > 0
    
    def test_api_key_authentication(self, test_server):
        """Test API key authentication."""
        # Get a valid API key
        api_keys = test_server.auth_manager.list_api_keys()
        assert len(api_keys) > 0
        
        valid_key = list(api_keys.keys())[0]
        
        # Test validation
        key_obj = test_server.auth_manager.validate_api_key(valid_key)
        assert key_obj.key == valid_key
        assert key_obj.is_active
    
    def test_service_registration(self, test_server):
        """Test service registration."""
        available_services = test_server.mcp_registry.list_available_services()
        assert "browseruse" in available_services
    
    def test_server_creation(self, test_server):
        """Test server creation and configuration."""
        assert test_server.config is not None
        assert test_server.auth_manager is not None
        assert test_server.mcp_registry is not None
        
        # Test app creation
        app = test_server.create_app()
        assert app is not None
