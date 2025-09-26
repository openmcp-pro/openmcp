"""Test cases for authentication and authorization."""

import pytest
from datetime import datetime, timedelta

from openmcp.core.auth import AuthManager, APIKey
from openmcp.core.config import AuthConfig


class TestAuthManager:
    """Test authentication manager."""
    
    @pytest.fixture
    def auth_config(self):
        """Create test auth configuration."""
        return AuthConfig(
            secret_key="test-secret-key-for-testing",
            algorithm="HS256",
            access_token_expire_minutes=30,
            allow_localhost=True,
            mock_api_key="openmcp-localhost-auth"
        )
    
    @pytest.fixture
    def auth_manager(self, auth_config):
        """Create test auth manager."""
        return AuthManager(auth_config)
    
    def test_create_api_key(self, auth_manager):
        """Test API key creation."""
        api_key = auth_manager.create_api_key("test-key", expires_days=30)
        
        assert api_key.startswith("bmcp_")
        assert len(api_key) > 20
        
        # Verify key is stored
        assert api_key in auth_manager.api_keys
        
        key_obj = auth_manager.api_keys[api_key]
        assert key_obj.name == "test-key"
        assert key_obj.is_active is True
        assert key_obj.expires_at is not None
    
    def test_validate_api_key(self, auth_manager):
        """Test API key validation."""
        # Create a valid key
        api_key = auth_manager.create_api_key("valid-key")
        
        # Test validation
        key_obj = auth_manager.validate_api_key(api_key)
        assert key_obj.key == api_key
        assert key_obj.name == "valid-key"
        assert key_obj.is_active is True
    
    def test_invalid_api_key(self, auth_manager):
        """Test invalid API key handling."""
        with pytest.raises(Exception):  # Should raise HTTPException
            auth_manager.validate_api_key("invalid-key")
    
    def test_revoke_api_key(self, auth_manager):
        """Test API key revocation."""
        # Create and revoke key
        api_key = auth_manager.create_api_key("revoke-test")
        
        success = auth_manager.revoke_api_key(api_key)
        assert success is True
        
        # Key should be inactive
        key_obj = auth_manager.api_keys[api_key]
        assert key_obj.is_active is False
        
        # Validation should fail
        with pytest.raises(Exception):
            auth_manager.validate_api_key(api_key)
    
    def test_check_permission(self, auth_manager):
        """Test permission checking."""
        # Create key with specific permissions
        api_key = auth_manager.create_api_key(
            "permission-test",
            permissions={"browseruse": True, "other_service": False}
        )
        
        # Test permissions
        assert auth_manager.check_permission(api_key, "browseruse") is True
        assert auth_manager.check_permission(api_key, "other_service") is False
        assert auth_manager.check_permission(api_key, "nonexistent") is False
    
    def test_list_api_keys(self, auth_manager):
        """Test listing API keys."""
        # Create multiple keys
        key1 = auth_manager.create_api_key("key1")
        key2 = auth_manager.create_api_key("key2")
        
        keys = auth_manager.list_api_keys()
        
        # Should include default key + our 2 keys
        assert len(keys) >= 3
        assert key1 in keys
        assert key2 in keys
    
    def test_create_access_token(self, auth_manager):
        """Test JWT token creation."""
        data = {"user": "test", "permissions": ["read", "write"]}
        token = auth_manager.create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long
    
    def test_verify_token(self, auth_manager):
        """Test JWT token verification."""
        data = {"user": "test", "permissions": ["read"]}
        token = auth_manager.create_access_token(data)
        
        # Verify token
        payload = auth_manager.verify_token(token)
        assert payload["user"] == "test"
        assert payload["permissions"] == ["read"]
        assert "exp" in payload  # Expiration should be set
    
    def test_expired_api_key(self, auth_manager):
        """Test expired API key handling."""
        # Create key that expires immediately
        api_key = auth_manager.create_api_key("expired-key", expires_days=0)
        
        # Manually set expiration to past
        key_obj = auth_manager.api_keys[api_key]
        key_obj.expires_at = datetime.utcnow() - timedelta(days=1)
        
        # Validation should fail
        with pytest.raises(Exception):
            auth_manager.validate_api_key(api_key)
    
    def test_localhost_bypass(self, auth_manager):
        """Test localhost authentication bypass."""
        # Test localhost IPs
        localhost_ips = ["127.0.0.1", "::1", "localhost"]
        
        for ip in localhost_ips:
            # Should create localhost API key
            key_obj = auth_manager.validate_api_key("any-key", client_ip=ip)
            assert key_obj.name == "localhost"
            assert key_obj.key == "localhost-bypass"
            assert key_obj.permissions["browseruse"] is True
            assert key_obj.permissions["web_search"] is True
            assert key_obj.permissions["web_crawler"] is True
    
    def test_mock_api_key(self, auth_manager):
        """Test mock API key functionality."""
        # Test mock API key
        key_obj = auth_manager.validate_api_key("openmcp-localhost-auth")
        assert key_obj.name == "mock"
        assert key_obj.key == "openmcp-localhost-auth"
        assert key_obj.permissions["browseruse"] is True
        assert key_obj.permissions["web_search"] is True
        assert key_obj.permissions["web_crawler"] is True
    
    def test_non_localhost_requires_auth(self, auth_manager):
        """Test that non-localhost IPs still require valid API keys."""
        # Non-localhost IP should fail without valid key
        with pytest.raises(Exception):
            auth_manager.validate_api_key("invalid-key", client_ip="192.168.1.1")
    
    def test_localhost_detection(self, auth_manager):
        """Test localhost IP detection."""
        # Test various localhost representations
        assert auth_manager._is_localhost("127.0.0.1") is True
        assert auth_manager._is_localhost("127.0.0.2") is True  # 127.x.x.x range
        assert auth_manager._is_localhost("::1") is True
        assert auth_manager._is_localhost("localhost") is True
        assert auth_manager._is_localhost("0.0.0.0") is True
        
        # Test non-localhost IPs
        assert auth_manager._is_localhost("192.168.1.1") is False
        assert auth_manager._is_localhost("10.0.0.1") is False
        assert auth_manager._is_localhost("8.8.8.8") is False
    
    def test_permission_check_with_localhost(self, auth_manager):
        """Test permission checking with localhost bypass."""
        # Test localhost permission check
        result = auth_manager.check_permission("any-key", "browseruse", client_ip="127.0.0.1")
        assert result is True
        
        # Test mock key permission check
        result = auth_manager.check_permission("openmcp-localhost-auth", "web_search")
        assert result is True


class TestAPIKey:
    """Test API key model."""
    
    def test_api_key_creation(self):
        """Test API key model creation."""
        api_key = APIKey(
            key="test-key",
            name="test",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30),
            is_active=True,
            permissions={"service1": True, "service2": False}
        )
        
        assert api_key.key == "test-key"
        assert api_key.name == "test"
        assert api_key.is_active is True
        assert api_key.permissions["service1"] is True
        assert api_key.permissions["service2"] is False
