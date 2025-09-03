"""Test cases for configuration management."""

import pytest
import tempfile
from pathlib import Path

from openmcp.core.config import Config, ServerConfig, AuthConfig, MCPServiceConfig


class TestConfig:
    """Test configuration management."""
    
    def test_default_config_creation(self):
        """Test creating default configuration."""
        config = Config.create_default()
        
        assert config.server.host == "0.0.0.0"
        assert config.server.port == 9000
        assert config.server.debug is False
        assert config.auth.secret_key is not None
        assert len(config.services) > 0
        
        # Check browseruse service is included
        browseruse_service = next(
            (s for s in config.services if s.name == "browseruse"), 
            None
        )
        assert browseruse_service is not None
        assert browseruse_service.enabled is True
    
    def test_config_serialization(self):
        """Test config save and load."""
        config = Config.create_default()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            # Save config
            config.save_to_file(temp_path)
            assert temp_path.exists()
            
            # Load config
            loaded_config = Config.from_file(temp_path)
            
            # Verify loaded config matches original
            assert loaded_config.server.host == config.server.host
            assert loaded_config.server.port == config.server.port
            assert loaded_config.auth.secret_key == config.auth.secret_key
            assert len(loaded_config.services) == len(config.services)
            
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_server_config(self):
        """Test server configuration."""
        server_config = ServerConfig(
            host="127.0.0.1",
            port=9000,
            debug=True,
            log_level="DEBUG"
        )
        
        assert server_config.host == "127.0.0.1"
        assert server_config.port == 9000
        assert server_config.debug is True
        assert server_config.log_level == "DEBUG"
    
    def test_auth_config(self):
        """Test authentication configuration."""
        auth_config = AuthConfig(
            secret_key="test-secret-key",
            algorithm="HS256",
            access_token_expire_minutes=60
        )
        
        assert auth_config.secret_key == "test-secret-key"
        assert auth_config.algorithm == "HS256"
        assert auth_config.access_token_expire_minutes == 60
    
    def test_mcp_service_config(self):
        """Test MCP service configuration."""
        service_config = MCPServiceConfig(
            name="test_service",
            enabled=True,
            config={"param1": "value1", "param2": 42}
        )
        
        assert service_config.name == "test_service"
        assert service_config.enabled is True
        assert service_config.config["param1"] == "value1"
        assert service_config.config["param2"] == 42
