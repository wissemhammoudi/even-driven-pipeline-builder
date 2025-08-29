import aiohttp
from typing import Optional, Dict, Any
from source.config.config import keycloak_config
import asyncio
import logging
import jwt
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class KeycloakAuthService:
    def __init__(self, session: aiohttp.ClientSession):
        self.config = keycloak_config
        self.session = session
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with Keycloak"""
        try:
            token_url = f"{self.config.server_url}/realms/{self.config.realm_name}/protocol/openid-connect/token"
            data = {
                "username": username,
                "password": password,
                "grant_type": "password",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret
            }
            
            logger.info(f"Attempting authentication for user: {username}")
            
            async with self.session.post(token_url, data=data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    token_data = await response.json()
                    logger.info(f"User {username} authenticated successfully")
                    return {
                        "access_token": token_data.get("access_token"),
                        "refresh_token": token_data.get("refresh_token"),
                        "expires_in": token_data.get("expires_in"),
                        "token_type": token_data.get("token_type")
                    }
                else:
                    error_data = await response.text()
                    logger.warning(f"Authentication failed for user {username}: {response.status} - {error_data}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Authentication timeout for user {username}")
            return None
        except Exception as e:
            logger.error(f"Authentication error for user {username}: {str(e)}")
            return None
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token with Keycloak"""
        try:
            # First try to decode the token to get basic info
            try:
                # Decode without verification to get payload
                decoded = jwt.decode(token, options={"verify_signature": False})
                
                # Check if token is expired
                exp = decoded.get("exp")
                if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                    logger.warning("Token is expired")
                    return None
                    
            except jwt.InvalidTokenError:
                logger.warning("Invalid JWT token format")
                return None
            
            # Now verify with Keycloak
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
                        logger.info(f"Token verified successfully for user: {token_info.get('preferred_username', 'unknown')}")
                        return {
                            "user_id": token_info.get("sub"),
                            "username": token_info.get("preferred_username"),
                            "email": token_info.get("email"),
                            "roles": token_info.get("realm_access", {}).get("roles", []),
                            "exp": token_info.get("exp"),
                            "iat": token_info.get("iat"),
                            "iss": token_info.get("iss")
                        }
                    else:
                        logger.warning("Token is not active")
                        return None
                else:
                    error_data = await response.text()
                    logger.warning(f"Token introspection failed: {response.status} - {error_data}")
                    return None
                
        except asyncio.TimeoutError:
            logger.error("Token verification timeout")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return None
    
    async def get_user_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user information from token"""
        try:
            userinfo_url = f"{self.config.server_url}/realms/{self.config.realm_name}/protocol/openid-connect/userinfo"
            headers = {"Authorization": f"Bearer {token}"}
            
            async with self.session.get(userinfo_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    user_info = await response.json()
                    logger.info(f"Retrieved user info for: {user_info.get('preferred_username', 'unknown')}")
                    return user_info
                else:
                    error_data = await response.text()
                    logger.warning(f"Failed to get user info: {response.status} - {error_data}")
                    return None
                
        except asyncio.TimeoutError:
            logger.error("User info retrieval timeout")
            return None
        except Exception as e:
            logger.error(f"User info retrieval error: {str(e)}")
            return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token"""
        try:
            token_url = f"{self.config.server_url}/realms/{self.config.realm_name}/protocol/openid-connect/token"
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret
            }
            
            async with self.session.post(token_url, data=data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    token_data = await response.json()
                    logger.info("Token refreshed successfully")
                    return {
                        "access_token": token_data.get("access_token"),
                        "refresh_token": token_data.get("refresh_token"),
                        "expires_in": token_data.get("expires_in"),
                        "token_type": token_data.get("token_type")
                    }
                else:
                    error_data = await response.text()
                    logger.warning(f"Token refresh failed: {response.status} - {error_data}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error("Token refresh timeout")
            return None
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return None
