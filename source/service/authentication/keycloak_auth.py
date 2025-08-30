from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from source.schema.user.schemas import UserRole
from source.service.keycloak_service import get_keycloak_service


security = HTTPBearer(auto_error=False)


class KeycloakAuthService:
    
    def __init__(self):
        self._keycloak_service = None

    async def _get_keycloak_service(self):
        if self._keycloak_service is None:
            self._keycloak_service = await get_keycloak_service()
        return self._keycloak_service
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        try:
            keycloak_service = await self._get_keycloak_service()
            return await keycloak_service.authenticate_user(username, password)
        except Exception:
            return None
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            keycloak_service = await self._get_keycloak_service()
            return await keycloak_service.verify_token(token)
        except Exception:
            return None
    
    async def get_user_info(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            keycloak_service = await self._get_keycloak_service()
            return await keycloak_service.get_user_info(token)
        except Exception:
            return None
    
    @staticmethod
    def get_user_role(roles: list) -> UserRole:
        if not roles:
            return UserRole.viewer
        if "admin" in roles:
            return UserRole.admin
        elif "user" in roles:
            return UserRole.user
        return UserRole.viewer


keycloak_auth_service = KeycloakAuthService()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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
    
    user_info["mapped_role"] = KeycloakAuthService.get_user_role(user_info.get("roles", []))
    return user_info


async def get_current_user_with_role(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    return current_user


async def require_admin_role(
    current_user: Dict[str, Any] = Depends(get_current_user_with_role)
) -> Dict[str, Any]:
    user_role = current_user.get("mapped_role")
    if user_role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Admin role required. Current role: {user_role}"
        )
    return current_user


async def require_user_role(
    current_user: Dict[str, Any] = Depends(get_current_user_with_role)
) -> Dict[str, Any]:
    if current_user.get("mapped_role") not in [UserRole.user, UserRole.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role required"
        )
    return current_user
