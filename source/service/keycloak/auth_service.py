import aiohttp
from typing import Optional, Dict
from source.config.config import keycloak_config
import asyncio

class KeycloakAuthService:
    def __init__(self, session: aiohttp.ClientSession):
        self.config = keycloak_config
        self.session = session
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        try:
            token_url = f"{self.config.server_url}/realms/{self.config.realm_name}/protocol/openid-connect/token"
            data = {
                "username": username,
                "password": password,
                "grant_type": "password",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret
            }
            
            async with self.session.post(token_url, data=data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    token_data = await response.json()
                    return {
                        "access_token": token_data.get("access_token"),
                        "refresh_token": token_data.get("refresh_token"),
                        "expires_in": token_data.get("expires_in"),
                        "token_type": token_data.get("token_type")
                    }
                else:
                    error_data = await response.text()
                    return None
                    
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            return None
    
    async def verify_token(self, token: str) -> Optional[Dict]:
        try:
            introspect_url = f"{self.config.server_url}/realms/{self.config.realm_name}/protocol/openid-connect/token/introspect"
            data = {
                "token": token,
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret
            }
            
            async with self.session.post(introspect_url, data=data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    token_info = await response.json()
                    if token_info.get("active", False):
                        return {
                            "user_id": token_info.get("sub"),
                            "username": token_info.get("preferred_username"),
                            "email": token_info.get("email"),
                            "roles": token_info.get("realm_access", {}).get("roles", []),
                            "exp": token_info.get("exp")
                        }
                return None
                
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            return None
    
    async def get_user_info(self, token: str) -> Optional[Dict]:
        try:
            userinfo_url = f"{self.config.server_url}/realms/{self.config.realm_name}/protocol/openid-connect/userinfo"
            headers = {"Authorization": f"Bearer {token}"}
            
            async with self.session.get(userinfo_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    return await response.json()
                return None
                
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            return None
