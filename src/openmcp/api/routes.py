"""API routes for openmcp."""

from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Header, status, Request
from fastapi.security import HTTPBearer

from ..core.auth import AuthManager, APIKey
from ..core.mcp_registry import MCPRegistry
from .models import (
    APIKeyRequest,
    APIKeyResponse,
    ServiceListResponse,
    ServiceInfo,
    ToolCallRequest,
    ToolCallResponse,
    ToolListResponse,
)

security = HTTPBearer()


def create_api_router(auth_manager: AuthManager, mcp_registry: MCPRegistry) -> APIRouter:
    """Create API router with dependencies."""
    
    router = APIRouter()
    
    async def get_current_api_key(
        request: Request,
        authorization: str = Header(None)
    ) -> APIKey:
        """Get current API key from Authorization header or allow localhost bypass."""
        # Get client IP address
        client_ip = request.client.host if request.client else None
        
        # If no authorization header, check if localhost is allowed
        if not authorization:
            if client_ip and auth_manager.config.allow_localhost and auth_manager._is_localhost(client_ip):
                return auth_manager._create_localhost_api_key()
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization header required"
                )
        
        # Extract token from "Bearer <token>" format
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid scheme")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format"
            )
        
        return auth_manager.validate_api_key(token, client_ip)
    
    @router.post("/auth/keys", response_model=APIKeyResponse)
    async def create_api_key(
        request: APIKeyRequest,
        current_key: APIKey = Depends(get_current_api_key)
    ):
        """Create a new API key."""
        # Only allow creating keys if current key has admin permissions
        # For now, we'll allow any valid key to create new keys
        api_key = auth_manager.create_api_key(
            request.name,
            request.expires_days,
            request.permissions
        )
        
        return APIKeyResponse(
            api_key=api_key,
            name=request.name,
            expires_days=request.expires_days
        )
    
    @router.get("/auth/keys")
    async def list_api_keys(current_key: APIKey = Depends(get_current_api_key)):
        """List all API keys (without revealing the actual keys)."""
        keys = auth_manager.list_api_keys()
        return {
            "keys": [
                {
                    "name": key_obj.name,
                    "created_at": key_obj.created_at,
                    "expires_at": key_obj.expires_at,
                    "is_active": key_obj.is_active,
                    "permissions": key_obj.permissions
                }
                for key_obj in keys.values()
            ]
        }
    
    @router.get("/services", response_model=ServiceListResponse)
    async def list_services(current_key: APIKey = Depends(get_current_api_key)):
        """List all available and running services."""
        available = mcp_registry.list_available_services()
        running = mcp_registry.list_services()
        
        service_details = {}
        for service_name in available:
            service = mcp_registry.get_service(service_name)
            if service:
                info = service.get_info()
                service_details[service_name] = ServiceInfo(
                    name=info["name"],
                    status="running" if info["running"] else "stopped",
                    tools=info["tools"],
                    config=info["config"]
                )
            else:
                service_details[service_name] = ServiceInfo(
                    name=service_name,
                    status="available",
                    tools=[],
                    config={}
                )
        
        return ServiceListResponse(
            available_services=available,
            running_services=running,
            service_details=service_details
        )
    
    @router.get("/services/{service_name}/tools", response_model=ToolListResponse)
    async def list_service_tools(
        service_name: str,
        request: Request,
        current_key: APIKey = Depends(get_current_api_key)
    ):
        """List tools available for a specific service."""
        # Get client IP for permission check
        client_ip = request.client.host if request.client else None
        
        # Check permission
        if not auth_manager.check_permission(current_key.key, service_name, client_ip):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No permission for service: {service_name}"
            )
        
        service = mcp_registry.get_service(service_name)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service not found or not running: {service_name}"
            )
        
        tools = service.get_tools()
        return ToolListResponse(service=service_name, tools=tools)
    
    @router.post("/services/{service_name}/call", response_model=ToolCallResponse)
    async def call_service_tool(
        service_name: str,
        tool_request: ToolCallRequest,
        request: Request,
        current_key: APIKey = Depends(get_current_api_key)
    ):
        """Call a tool on a specific service."""
        # Get client IP for permission check
        client_ip = request.client.host if request.client else None
        
        # Check permission
        if not auth_manager.check_permission(current_key.key, service_name, client_ip):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No permission for service: {service_name}"
            )
        
        service = mcp_registry.get_service(service_name)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service not found or not running: {service_name}"
            )
        
        try:
            result = await service.call_tool(
                tool_request.tool_name,
                tool_request.arguments,
                tool_request.session_id
            )
            
            # Check if result contains an error
            if "error" in result:
                return ToolCallResponse(
                    success=False,
                    result=result,
                    session_id=result.get("session_id", tool_request.session_id),
                    error=result["error"]
                )
            
            return ToolCallResponse(
                success=True,
                result=result,
                session_id=result.get("session_id", tool_request.session_id)
            )
        
        except Exception as e:
            return ToolCallResponse(
                success=False,
                result={},
                session_id=tool_request.session_id,
                error=str(e)
            )
    
    @router.get("/services/{service_name}/status")
    async def get_service_status(
        service_name: str,
        current_key: APIKey = Depends(get_current_api_key)
    ):
        """Get status of a specific service."""
        return mcp_registry.get_service_status(service_name)
    
    return router
