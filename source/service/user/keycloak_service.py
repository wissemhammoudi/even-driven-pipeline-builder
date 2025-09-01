from source.schema.user.schemas import UserCreate, UserUpdate


class UserKeycloakService:
    def __init__(self):
        self._keycloak_service = None
    
    async def _get_keycloak_service(self):
        if self._keycloak_service is None:
            from source.service.keycloak_service import get_keycloak_service
            self._keycloak_service = await get_keycloak_service()
        return self._keycloak_service
    
    async def create_user(self, user_data: UserCreate) -> str:

        try:
            if not user_data.username or not user_data.email or not user_data.password:
                raise ValueError("Username, email, and password are required")
                            
            keycloak_service = await self._get_keycloak_service()
            user_id = await keycloak_service.create_user(
                username=user_data.username,
                email=user_data.email,
                first_name=user_data.first_name or "",
                last_name=user_data.last_name or "",
                password=user_data.password,
                role=user_data.role.value if user_data.role else "user"
            )
            
            if user_id:
                return user_id
            else:
                raise Exception("Failed to create user in Keycloak - no user ID returned")
                
        except ValueError as e:
            raise Exception(f"Keycloak user creation failed: {str(e)}")


    async def update_user(self, user_data: UserUpdate) -> bool:

        try:
            if not user_data.user_id:
                raise ValueError("User ID is required for update")
                
            keycloak_service = await self._get_keycloak_service()
            success = await keycloak_service.update_user(
                user_data.user_id,  # user_id as first positional argument
                username=user_data.username if user_data.username is not None else None,
                email=user_data.email if user_data.email is not None else None,
                first_name=user_data.first_name if user_data.first_name is not None else None,
                last_name=user_data.last_name if user_data.last_name is not None else None,
                role=user_data.role.value if user_data.role is not None else None
            )
            
            if success:
                return success
            else:
                raise Exception("Failed to update user in Keycloak - no success returned")
                
        except ValueError as e:
            raise Exception(f"Invalid input for Keycloak user update: {str(e)}")
        except Exception as e:
            raise Exception(f"Keycloak user update failed: {str(e)}")

    async def delete_user(self, user_id: str) -> bool:

        try:
            if not user_id:
                raise ValueError("User ID is required for deletion")
                
            keycloak_service = await self._get_keycloak_service()
            success = await keycloak_service.delete_user(user_id)
            
            if success:
                return success
            else:
                raise Exception("Failed to delete user in Keycloak - no success returned")
                
            return success
                
        except ValueError as e:
            raise Exception(f"Invalid input for Keycloak user deletion: {str(e)}")
        except Exception as e:
            raise Exception(f"Keycloak user deletion failed: {str(e)}")

    async def get_user_id_by_username(self, username: str) -> str:

        try:
            if not username:
                raise ValueError("Username is required")
                
            keycloak_service = await self._get_keycloak_service()
            user_id = await keycloak_service.get_user_id_by_username(username)
            
            if user_id: 
                return user_id
            else:
                raise Exception("No Keycloak user ID found for username")
        except ValueError as e:
            raise Exception(f"Invalid input for getting Keycloak user ID: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to get Keycloak user ID: {str(e)}")

    async def authenticate_user(self, username: str, password: str) -> dict:
        """
        Authenticate a user with Keycloak
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            Authentication result with tokens
            
        Raises:
            Exception: If authentication fails
        """
        try:
            if not username or not password:
                raise ValueError("Username and password are required")
                
            logger.debug(f"Authenticating user {username} with Keycloak")
            
            auth_result = await self.keycloak_service.authenticate_user(username, password)
            
            if auth_result:
                logger.info(f"User {username} authenticated successfully with Keycloak")
                return auth_result
            else:
                logger.warning(f"Authentication failed for user {username}")
                return None
                
        except ValueError as e:
            logger.error(f"Invalid input for authentication: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Authentication failed for user {username}: {str(e)}")
            raise Exception(f"Authentication failed: {str(e)}")
