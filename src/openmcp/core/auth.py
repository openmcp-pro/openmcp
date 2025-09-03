"""Authentication and authorization for openmcp."""

import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from .config import AuthConfig


class APIKey(BaseModel):
    """API key model."""
    
    key: str
    name: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    permissions: Dict[str, bool] = {}


class AuthManager:
    """Manages authentication and API keys."""
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.api_keys: Dict[str, APIKey] = {}
        
        # Create a default API key for testing
        self.create_api_key("default", expires_days=365)
    
    def create_api_key(
        self, 
        name: str, 
        expires_days: Optional[int] = None,
        permissions: Optional[Dict[str, bool]] = None
    ) -> str:
        """Create a new API key."""
        key = f"bmcp_{secrets.token_urlsafe(32)}"
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        api_key = APIKey(
            key=key,
            name=name,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            permissions=permissions or {"browseruse": True}
        )
        
        self.api_keys[key] = api_key
        return key
    
    def validate_api_key(self, api_key: str) -> APIKey:
        """Validate an API key."""
        if api_key not in self.api_keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        key_obj = self.api_keys[api_key]
        
        if not key_obj.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key is inactive"
            )
        
        if key_obj.expires_at and datetime.utcnow() > key_obj.expires_at:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has expired"
            )
        
        return key_obj
    
    def check_permission(self, api_key: str, service: str) -> bool:
        """Check if API key has permission for a service."""
        key_obj = self.validate_api_key(api_key)
        return key_obj.permissions.get(service, False)
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke an API key."""
        if api_key in self.api_keys:
            self.api_keys[api_key].is_active = False
            return True
        return False
    
    def list_api_keys(self) -> Dict[str, APIKey]:
        """List all API keys."""
        return self.api_keys.copy()
    
    def create_access_token(self, data: dict) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=self.config.access_token_expire_minutes
        )
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            self.config.secret_key, 
            algorithm=self.config.algorithm
        )
        return encoded_jwt
    
    def verify_token(self, token: str) -> dict:
        """Verify JWT token."""
        try:
            payload = jwt.decode(
                token, 
                self.config.secret_key, 
                algorithms=[self.config.algorithm]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
