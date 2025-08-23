from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict
from source.service.keycloak_service import get_keycloak_service
from source.schema.user.schemas import UserRole

security = HTTPBearer()

class KeycloakAuthService:
    """Authentication service using Keycloak"""
    
    def __init__(self):
        self.keycloak_service = get_keycloak_service()
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user with Keycloak"""
        try:
            return await self.keycloak_service.authenticate_user(username, password)
        except Exception as e:
            return None
    
    async def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token with Keycloak"""
        try:
            return await self.keycloak_service.verify_token(token)
        except Exception as e:
            return None
    
    async def get_user_info(self, token: str) -> Optional[Dict]:
        """Get user information from token"""
        try:
            return await self.keycloak_service.get_user_info(token)
        except Exception as e:
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

keycloak_auth_service = KeycloakAuthService()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Dependency to get current authenticated user"""
    try:
        token = credentials.credentials
        user_info = await keycloak_auth_service.verify_token(token)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_info
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_with_role(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Dependency to get current authenticated user with mapped role"""
    user_info = await get_current_user(credentials)
    
    mapped_role = keycloak_auth_service.get_user_role(user_info.get("roles", []))
    user_info["mapped_role"] = mapped_role
    
    return user_info

async def require_admin_role(current_user: Dict = Depends(get_current_user_with_role)) -> Dict:
    """Dependency to require admin role"""
    user_role = current_user.get("mapped_role")
    
    if user_role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Admin role required. Current role: {user_role}"
        )
    
    return current_user

async def require_user_role(current_user: Dict = Depends(get_current_user_with_role)) -> Dict:
    """Dependency to require user or admin role"""
    if current_user.get("mapped_role") not in [UserRole.user, UserRole.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role required"
        )
    return current_user
