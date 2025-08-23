import logging
from typing import Optional
from source.schema.user.schemas import UserCreate, UserUpdate
from source.service.keycloak_service import get_keycloak_service

# Configure logging
logger = logging.getLogger(__name__)

class UserKeycloakService:
    def __init__(self):
        self.keycloak_service = get_keycloak_service()
    
    async def create_user(self, user_data: UserCreate) -> str:
        """
        Create a new user in Keycloak
        
        Args:
            user_data: User creation data
            
        Returns:
            Keycloak user ID
            
        Raises:
            Exception: If user creation fails
        """
        try:
            if not user_data.username or not user_data.email or not user_data.password:
                raise ValueError("Username, email, and password are required")
                
            logger.info(f"Creating user {user_data.username} in Keycloak")
            
            user_id = await self.keycloak_service.create_user(
                username=user_data.username,
                email=user_data.email,
                first_name=user_data.first_name or "",
                last_name=user_data.last_name or "",
                password=user_data.password,
                role=user_data.role.value if user_data.role else "user"
            )
            
            if user_id:
                logger.info(f"User {user_data.username} created successfully in Keycloak with ID: {user_id}")
                return user_id
            else:
                raise Exception("Failed to create user in Keycloak - no user ID returned")
                
        except ValueError as e:
            logger.error(f"Invalid input for Keycloak user creation: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Keycloak user creation failed for {user_data.username}: {str(e)}")
            raise Exception(f"Keycloak user creation failed: {str(e)}")

    async def update_user(self, user_data: UserUpdate) -> bool:
        """
        Update an existing user in Keycloak
        
        Args:
            user_data: User update data
            
        Returns:
            True if update successful
            
        Raises:
            Exception: If user update fails
        """
        try:
            if not user_data.user_id:
                raise ValueError("User ID is required for update")
                
            logger.info(f"Updating user {user_data.user_id} in Keycloak")
            
            success = await self.keycloak_service.update_user(
                user_id=user_data.user_id,
                username=user_data.username,
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name
            )
            
            if success:
                logger.info(f"User {user_data.user_id} updated successfully in Keycloak")
            else:
                logger.warning(f"User {user_data.user_id} update in Keycloak returned False")
                
            return success
                
        except ValueError as e:
            logger.error(f"Invalid input for Keycloak user update: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Keycloak user update failed for {user_data.user_id}: {str(e)}")
            raise Exception(f"Keycloak user update failed: {str(e)}")

    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user from Keycloak
        
        Args:
            user_id: Keycloak user ID
            
        Returns:
            True if deletion successful
            
        Raises:
            Exception: If user deletion fails
        """
        try:
            if not user_id:
                raise ValueError("User ID is required for deletion")
                
            logger.info(f"Deleting user {user_id} from Keycloak")
            
            success = await self.keycloak_service.delete_user(user_id)
            
            if success:
                logger.info(f"User {user_id} deleted successfully from Keycloak")
            else:
                logger.warning(f"User {user_id} deletion in Keycloak returned False")
                
            return success
                
        except ValueError as e:
            logger.error(f"Invalid input for Keycloak user deletion: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Keycloak user deletion failed for {user_id}: {str(e)}")
            raise Exception(f"Keycloak user deletion failed: {str(e)}")

    async def get_user_id_by_username(self, username: str) -> str:
        """
        Get Keycloak user ID by username
        
        Args:
            username: User's username
            
        Returns:
            Keycloak user ID
            
        Raises:
            Exception: If retrieval fails
        """
        try:
            if not username:
                raise ValueError("Username is required")
                
            logger.debug(f"Getting Keycloak user ID for username: {username}")
            
            user_id = await self.keycloak_service.get_user_id_by_username(username)
            
            if user_id:
                logger.debug(f"Found Keycloak user ID {user_id} for username {username}")
                return user_id
            else:
                logger.warning(f"No Keycloak user ID found for username {username}")
                return ""
                
        except ValueError as e:
            logger.error(f"Invalid input for getting Keycloak user ID: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to get Keycloak user ID for username {username}: {str(e)}")
            raise Exception(f"Failed to get Keycloak user ID: {str(e)}")
