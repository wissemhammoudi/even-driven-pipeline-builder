import asyncio
import aiohttp
from typing import Optional
from source.config.config import keycloak_config, application_user_init_config
from source.models.user.models import User
from source.schema.user.schemas import UserRole
from source.repository.user.repository import UserRepository

class KeycloakUserService:
    def __init__(self, session: aiohttp.ClientSession, setup_service):
        self.config = keycloak_config
        self.session = session
        self.setup_service = setup_service
        
    async def create_admin_user(self) -> bool:
        try:
            admin_token = await self.setup_service.get_admin_token()
            if not admin_token:
                return False
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            search_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users?username={application_user_init_config.admin_username}"
            async with self.session.get(search_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    users = await response.json()
                    if users:
                        return True
            
            user_data = {
                "username": application_user_init_config.admin_username,
                "email": application_user_init_config.admin_email,
                "firstName": application_user_init_config.admin_first_name,
                "lastName": application_user_init_config.admin_last_name,
                "enabled": True,
                "emailVerified": True,
                "credentials": [{
                    "type": "password",
                    "value": application_user_init_config.admin_password,
                    "temporary": False
                }]
            }
            
            user_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users"
            async with self.session.post(user_url, headers=headers, json=user_data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 201:
                    user_id = response.headers.get("Location", "").split("/")[-1]
                    
                    role_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users/{user_id}/role-mappings/realm"
                    admin_role = await self.setup_service._get_role_id("admin")
                    if admin_role:
                        role_data = [{"id": admin_role, "name": "admin"}]
                        async with self.session.post(role_url, headers=headers, json=role_data, timeout=aiohttp.ClientTimeout(total=30)) as role_response:
                            if role_response.status == 204:
                                return True
                    
                    return True
                else:
                    return False
                    
        except asyncio.TimeoutError:
            return False
        except Exception as e:
            return False
    
    async def create_local_admin_user(self) -> bool:
        try:
            user_repository = UserRepository()
            
            try:
                existing_user = user_repository.get_user_by_username(
                    application_user_init_config.admin_username
                )
                if existing_user:
                    return True
            except:
                pass
            
            admin_token = await self.setup_service.get_admin_token()
            if not admin_token:
                return False
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            search_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users?username={application_user_init_config.admin_username}"
            async with self.session.get(search_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    users = await response.json()
                    if users:
                        keycloak_user_id = users[0].get("id")
                        
                        user = User(
                            user_id=keycloak_user_id,
                            username=application_user_init_config.admin_username,
                            email=application_user_init_config.admin_email,
                            first_name=application_user_init_config.admin_first_name,
                            last_name=application_user_init_config.admin_last_name,
                            role=UserRole.admin
                        )
                        
                        user_repository.create_user(user)
                        return True
                    else:
                        return False
                else:
                    return False
            
        except asyncio.TimeoutError:
            return False
        except Exception as e:
            return False
    
    async def create_demo_users(self) -> bool:
        try:
            demo_users = application_user_init_config.demo_users
            
            admin_token = await self.setup_service.get_admin_token()
            if not admin_token:
                return False
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            created_count = 0
            for user_data in demo_users:
                try:
                    keycloak_user_data = {
                        "username": user_data["username"],
                        "email": user_data["email"],
                        "firstName": user_data["first_name"],
                        "lastName": user_data["last_name"],
                        "enabled": True,
                        "emailVerified": True,
                        "credentials": [{
                            "type": "password",
                            "value": user_data["password"],
                            "temporary": False
                        }]
                    }
                    
                    user_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users"
                    async with self.session.post(user_url, headers=headers, json=keycloak_user_data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        if response.status == 201:
                            user_id = response.headers.get("Location", "").split("/")[-1]
                            
                            role_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users/{user_id}/role-mappings/realm"
                            role = await self.setup_service._get_role_id(user_data["role"])
                            if role:
                                role_data = [{"id": role, "name": user_data["role"]}]
                                async with self.session.post(role_url, headers=headers, json=role_data, timeout=aiohttp.ClientTimeout(total=30)) as role_response:
                                    if role_response.status == 204:
                                        created_count += 1
                                    else:
                                        created_count += 1
                            else:
                                created_count += 1
                        else:
                            pass
                            
                except Exception as e:
                    pass
            
            return created_count > 0
            
        except asyncio.TimeoutError:
            return False
        except Exception as e:
            return False

    async def create_user(self, username: str, email: str, first_name: str, last_name: str, password: str, role: str) -> Optional[str]:
        try:
            admin_token = await self.setup_service.get_admin_token()
            if not admin_token:
                return None
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            keycloak_user_data = {
                "username": username,
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "enabled": True,
                "emailVerified": True,
                "credentials": [{
                    "type": "password",
                    "value": password,
                    "temporary": False
                }]
            }
            
            search_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users?username={username}"
            async with self.session.get(search_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as search_response:
                if search_response.status == 200:
                    existing_users = await search_response.json()
                    if existing_users:
                        return existing_users[0].get("id")
            
            user_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users"
            async with self.session.post(user_url, headers=headers, json=keycloak_user_data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 201:
                    user_id = response.headers.get("Location", "").split("/")[-1]
                    
                    role_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users/{user_id}/role-mappings/realm"
                    role_id = await self.setup_service._get_role_id(role)
                    if role_id:
                        role_data = [{"id": role_id, "name": role}]
                        async with self.session.post(role_url, headers=headers, json=role_data, timeout=aiohttp.ClientTimeout(total=30)) as role_response:
                            if role_response.status == 204:
                                return user_id
                            else:
                                return user_id
                    else:
                        return user_id
                else:
                    return None
                    
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            return None

    async def update_user(self, user_id: str, username: str = None, email: str = None, first_name: str = None, last_name: str = None, role: str = None) -> bool:
        try:
            admin_token = await self.setup_service.get_admin_token()
            if not admin_token:
                return False
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            update_data = {}
            if username is not None:
                update_data["username"] = username
            if email is not None:
                update_data["email"] = email
            if first_name is not None:
                update_data["firstName"] = first_name
            if last_name is not None:
                update_data["lastName"] = last_name
            
            if not update_data:
                return True  
            
            user_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users/{user_id}"
            async with self.session.put(user_url, headers=headers, json=update_data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 204:
                    # If role is provided, update the user's role
                    if role is not None:
                        await self.update_user_role(user_id, role)
                    return True
                else:
                    return False
                    
        except asyncio.TimeoutError:
            return False
        except Exception as e:
            return False

    async def update_user_role(self, user_id: str, role: str) -> bool:

        try:
            admin_token = await self.setup_service.get_admin_token()
            if not admin_token:
                return False
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            role_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/roles/{role}"
            async with self.session.get(role_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    return False
                
                role_data = await response.json()
                role_id = role_data.get("id")
                
                if not role_id:
                    return False
            
            user_roles_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users/{user_id}/role-mappings/realm"
            async with self.session.delete(user_roles_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status not in [200, 204]:
                    return False
            
            add_role_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users/{user_id}/role-mappings/realm"
            role_mapping = [{"id": role_id, "name": role}]
            
            async with self.session.post(add_role_url, headers=headers, json=role_mapping, timeout=aiohttp.ClientTimeout(total=30)) as response:
                return response.status in [200, 204]
                
        except asyncio.TimeoutError:
            return False
        except Exception as e:
            return False

    async def delete_user(self, user_id: str) -> bool:
        try:
            admin_token = await self.setup_service.get_admin_token()
            if not admin_token:
                return False
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            user_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users/{user_id}"
            async with self.session.delete(user_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                
                if response.status == 204:
                    return True
                else:
                    response_text = await response.text()
                    return False
                    
        except asyncio.TimeoutError:
            return False
        except Exception as e:
            return False

    async def get_user_id_by_username(self, username: str) -> Optional[str]:
        try:
            admin_token = await self.setup_service.get_admin_token()
            if not admin_token:
                return None
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            search_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users?username={username}"
            async with self.session.get(search_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    users = await response.json()
                    if users:
                        return users[0].get("id")
                    else:
                        return None
                else:
                    return None
                    
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            return None
