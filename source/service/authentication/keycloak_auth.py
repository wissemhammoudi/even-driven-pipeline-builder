from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from source.schema.user.schemas import UserRole
import logging

# Configure logging
logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

class KeycloakAuthService:
    """Authentication service using Keycloak"""
    
    def __init__(self):
        self._keycloak_service = None
    
    async def _get_keycloak_service(self):
        """Get keycloak service instance when needed"""
        if self._keycloak_service is None:
            from source.service.keycloak_service import get_keycloak_service
            self._keycloak_service = await get_keycloak_service()
        return self._keycloak_service
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with Keycloak"""
        try:
            keycloak_service = await self._get_keycloak_service()
            return await keycloak_service.authenticate_user(username, password)
        except Exception as e:
            logger.error(f"Authentication failed for user {username}: {str(e)}")
            return None
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token with Keycloak"""
        try:
            keycloak_service = await self._get_keycloak_service()
            return await keycloak_service.verify_token(token)
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return None
    
    async def get_user_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user information from token"""
        try:
            keycloak_service = await self._get_keycloak_service()
            return await keycloak_service.get_user_info(token)
        except Exception as e:
            logger.error(f"Failed to get user info: {str(e)}")
            return None
    
    def get_user_role(self, roles: list) -> UserRole:
        """Map Keycloak roles to application roles"""
        if not roles:
            return UserRole.viewer
            
        if "admin" in roles:
            return UserRole.admin
        elif "user" in roles:
            return UserRole.user
        else:
            return UserRole.viewer

# Global instance
keycloak_auth_service = KeycloakAuthService()

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """Dependency to get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_info = await keycloak_auth_service.verify_token(token)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_info["mapped_role"] = keycloak_auth_service.get_user_role(user_info.get("roles", []))
        
        logger.info(f"User authenticated: {user_info.get('username', 'unknown')}")
        return user_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_with_role(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Dependency to get current authenticated user with mapped role"""
    return current_user

async def require_admin_role(current_user: Dict[str, Any] = Depends(get_current_user_with_role)) -> Dict[str, Any]:
    """Dependency to require admin role"""
    user_role = current_user.get("mapped_role")
    
    if user_role != UserRole.admin:
        logger.warning(f"Access denied: user {current_user.get('username')} requires admin role, has {user_role}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Admin role required. Current role: {user_role}"
        )
    
    return current_user

async def require_user_role(current_user: Dict[str, Any] = Depends(get_current_user_with_role)) -> Dict[str, Any]:
    """Dependency to require user or admin role"""
    if current_user.get("mapped_role") not in [UserRole.user, UserRole.admin]:
        logger.warning(f"Access denied: user {current_user.get('username')} requires user role, has {current_user.get('mapped_role')}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role required"
        )
    return current_user
