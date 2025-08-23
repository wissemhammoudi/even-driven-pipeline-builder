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
        return await self.keycloak_service.authenticate_user(username, password)
    
    async def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token with Keycloak"""
        return await self.keycloak_service.verify_token(token)
    
    async def get_user_info(self, token: str) -> Optional[Dict]:
        """Get user information from token"""
        return await self.keycloak_service.get_user_info(token)
    
    def get_user_role(self, roles: list) -> UserRole:
        """Map Keycloak roles to application roles"""
        print(f"DEBUG: Mapping roles: {roles}")
        print(f"DEBUG: Role types: {[type(role) for role in roles]}")
        
        if "admin" in roles:
            print(f"DEBUG: Found admin role")
            return UserRole.admin
        elif "user" in roles:
            print(f"DEBUG: Found user role")
            return UserRole.user
        else:
            print(f"DEBUG: No matching role found, defaulting to viewer")
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
    
    print(f"DEBUG: get_current_user_with_role - user_info from token: {user_info}")
    print(f"DEBUG: get_current_user_with_role - roles from token: {user_info.get('roles', [])}")
    
    mapped_role = keycloak_auth_service.get_user_role(user_info.get("roles", []))
    user_info["mapped_role"] = mapped_role
    
    print(f"DEBUG: get_current_user_with_role - Mapped role: {mapped_role}")
    print(f"DEBUG: get_current_user_with_role - Final user_info: {user_info}")
    
    return user_info

async def require_admin_role(current_user: Dict = Depends(get_current_user_with_role)) -> Dict:
    """Dependency to require admin role"""
    print(f"DEBUG: require_admin_role - current_user: {current_user}")
    print(f"DEBUG: require_admin_role - mapped_role: {current_user.get('mapped_role')}")
    print(f"DEBUG: require_admin_role - UserRole.admin: {UserRole.admin}")
    
    user_role = current_user.get("mapped_role")
    
    if user_role != UserRole.admin:
        print(f"DEBUG: require_admin_role - Access denied, role mismatch")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Admin role required. Current role: {user_role}"
        )
    
    print(f"DEBUG: require_admin_role - Access granted")
    return current_user

async def require_user_role(current_user: Dict = Depends(get_current_user_with_role)) -> Dict:
    """Dependency to require user or admin role"""
    if current_user.get("mapped_role") not in [UserRole.user, UserRole.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role required"
        )
    return current_user
