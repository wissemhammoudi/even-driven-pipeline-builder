import logging
from typing import Dict, Any, Optional
from source.repository.user.repository import UserRepository
from source.schema.user.schemas import UserCreate, UserUpdate, UserResponse, PasswordUpdate, LoginSchema, UserRole
from source.exceptions.exceptions import UserNotFoundError, DuplicateUserError, InvalidPasswordError
from source.models.user.models import User
from source.service.authentication.keycloak_auth import keycloak_auth_service
from .keycloak_service import UserKeycloakService
from .superset_service import UserSupersetService
from .initialization_service import UserInitializationService

# Configure logging
logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.keycloak_service = UserKeycloakService()
        self.superset_service = UserSupersetService()
        self.initialization_service = UserInitializationService()
    
    async def signup(self, user_data: UserCreate) -> Dict[str, Any]:
        """
        Create a new user in Keycloak, local database, and Superset
        
        Args:
            user_data: User creation data
            
        Returns:
            Dict containing success message and user ID
            
        Raises:
            DuplicateUserError: If username or email already exists
            Exception: If user creation fails
        """
        try:
            # Check for existing user
            existing_user = self.user_repository.get_user_by_email_and_username(
                user_data.email, user_data.username
            )
            if existing_user:
                raise DuplicateUserError("Username or email already exists")
            
            # Create user in Keycloak
            keycloak_user_id = await self.keycloak_service.create_user(user_data)
            if not keycloak_user_id:
                raise Exception("Failed to create user in Keycloak")
            
            # Create user in local database
            user = User(
                user_id=keycloak_user_id,  
                username=user_data.username,
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                role=user_data.role or UserRole.user
            )
            created_user = self.user_repository.create_user(user)
            
            # Create user in Superset (non-blocking)
            try:
                superset_user_id = self.superset_service.create_user(
                    username=user_data.username,
                    email=user_data.email,
                    first_name=user_data.first_name or "",
                    last_name=user_data.last_name or "",
                    role=user_data.role or UserRole.user
                )
                
                if superset_user_id:
                    self.superset_service.add_user_association(
                        user_id=keycloak_user_id, 
                        superset_user_id=superset_user_id
                    )
                    logger.info(f"User {user_data.username} created in Superset with ID: {superset_user_id}")
                else:
                    logger.warning(f"Failed to create user {user_data.username} in Superset")
                    
            except Exception as e:
                # Log the error but don't fail the user creation
                logger.error(f"Failed to create Superset user for {user_data.username}: {str(e)}")
            
            logger.info(f"User {user_data.username} created successfully with ID: {keycloak_user_id}")
            return {
                "message": "User created successfully in Keycloak and local database",
                "user_id": keycloak_user_id,
                "username": user_data.username,
                "email": user_data.email
            }
            
        except DuplicateUserError:
            raise
        except Exception as e:
            logger.error(f"Failed to create user {user_data.username}: {str(e)}")
            raise Exception(f"Failed to create user: {str(e)}")

    def get_all_users(self) -> list:
        """Get all active users"""
        try:
            return self.user_repository.get_all_active_user()
        except Exception as e:
            logger.error(f"Failed to get all users: {str(e)}")
            raise
    
    def get_all_users_filtered(self, search: str = None, role: str = None, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Get all users with filtering and pagination
        
        Args:
            search: Search term for username, email, first_name, or last_name
            role: Filter by user role
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            Dict containing users, total count, and pagination info
        """
        try:
            if limit <= 0 or limit > 1000:
                limit = 100
            if offset < 0:
                offset = 0
                
            return self.user_repository.get_all_users_filtered(
                search=search, role=role, limit=limit, offset=offset
            )
        except Exception as e:
            logger.error(f"Failed to get filtered users: {str(e)}")
            raise
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            User object or None if not found
        """
        try:
            if not user_id:
                raise ValueError("User ID cannot be empty")
            return self.user_repository.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {str(e)}")
            raise
    
    def get_user_by_username(self, username: str) -> User:
        """
        Get active user by username
        
        Args:
            username: User's username
            
        Returns:
            User object
            
        Raises:
            UserNotFoundError: If user not found or inactive
        """
        try:
            if not username:
                raise ValueError("Username cannot be empty")
                
            user = self.user_repository.get_active_user_by_username(username)
            if not user:
                raise UserNotFoundError(f"User with username '{username}' not found")
            return user
        except UserNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get user by username {username}: {str(e)}")
            raise

    async def delete_user(self, user_id: str) -> Dict[str, str]:
        """
        Delete user from Keycloak first, then sync to local DB
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            Success message
            
        Raises:
            UserNotFoundError: If user not found
            Exception: If deletion fails
        """
        try:
            if not user_id:
                raise ValueError("User ID cannot be empty")
                
            user = self.user_repository.get_active_user_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"User with ID {user_id} not found")
            
            # Delete from Keycloak first
            await self.keycloak_service.delete_user(user_id)
            
            # Mark as deleted in local database
            self.user_repository.mark_deleted(user)
            
            logger.info(f"User {user_id} deleted successfully")
            return {"message": "User deleted successfully from Keycloak and local database"}
            
        except UserNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {str(e)}")
            raise Exception(f"Failed to delete user: {str(e)}")

    def update_password(self, password_data: PasswordUpdate) -> None:
        """
        Update user password (redirects to Keycloak)
        
        Args:
            password_data: Password update data
            
        Raises:
            UserNotFoundError: If user not found
            InvalidPasswordError: Always raised (password changes through Keycloak)
        """
        try:
            if not password_data.user_id:
                raise ValueError("User ID cannot be empty")
                
            user = self.user_repository.get_active_user_by_id(password_data.user_id)
            if not user:
                raise UserNotFoundError(f"User with ID {password_data.user_id} not found")

            raise InvalidPasswordError("Password changes must be done through Keycloak")
            
        except UserNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update password for user {password_data.user_id}: {str(e)}")
            raise

    async def update_user(self, user_data: UserUpdate) -> Dict[str, str]:
        """
        Update user in Keycloak first, then sync to local DB
        
        Args:
            user_data: User update data
            
        Returns:
            Success message
            
        Raises:
            UserNotFoundError: If user not found
            DuplicateUserError: If email or username already exists
            Exception: If update fails
        """
        try:
            if not user_data.user_id:
                raise ValueError("User ID cannot be empty")
                
            user = self.user_repository.get_user_by_id(user_data.user_id)
            if not user:
                raise UserNotFoundError(f"User with ID {user_data.user_id} not found")
            
            # Check for duplicate email
            if user_data.email:
                existing_email = self.user_repository.get_user_by_email(user_data.email)
                if existing_email and existing_email.user_id != user.user_id:
                    raise DuplicateUserError("Email already exists")
            
            # Check for duplicate username
            if user_data.username:
                existing_username = self.user_repository.get_user_by_username(user_data.username)
                if existing_username and existing_username.user_id != user.user_id:
                    raise DuplicateUserError("Username already exists")
            
            # Update in Keycloak first
            await self.keycloak_service.update_user(user_data)
            
            # Update local database
            if user_data.email:
                user.email = user_data.email
            if user_data.username:
                user.username = user_data.username
            if user_data.first_name:
                user.first_name = user_data.first_name
            if user_data.last_name:
                user.last_name = user_data.last_name
            
            self.user_repository.commit()
            
            logger.info(f"User {user_data.user_id} updated successfully")
            return {"message": "User information updated successfully in Keycloak and local database"}
            
        except (UserNotFoundError, DuplicateUserError):
            raise
        except Exception as e:
            logger.error(f"Failed to update user {user_data.user_id}: {str(e)}")
            raise Exception(f"Failed to update user: {str(e)}")

    async def login(self, login_data: LoginSchema) -> Dict[str, Any]:
        """
        Login using Keycloak authentication
        
        Args:
            login_data: Login credentials
            
        Returns:
            Authentication tokens and metadata
            
        Raises:
            InvalidPasswordError: If authentication fails
        """
        try:
            if not login_data.username or not login_data.password:
                raise InvalidPasswordError("Username and password are required")
                
            # Authenticate with Keycloak
            auth_result = await keycloak_auth_service.authenticate_user(
                login_data.username, 
                login_data.password
            )
            
            if not auth_result:
                raise InvalidPasswordError("Invalid username or password")  
            
            # Verify user exists in local database
            user = self.user_repository.get_active_user_by_username(login_data.username)
            if not user:
                logger.warning(f"User {login_data.username} authenticated with Keycloak but not found in local DB")
                raise InvalidPasswordError("User account not found")
            
            logger.info(f"User {login_data.username} logged in successfully")
            return {
                "access_token": auth_result["access_token"],
                "refresh_token": auth_result["refresh_token"],
                "token_type": auth_result["token_type"],
                "expires_in": auth_result["expires_in"],
                "user_id": user.user_id,
                "username": user.username,
                "role": user.role.value
            }
            
        except InvalidPasswordError:
            raise
        except Exception as e:
            logger.error(f"Login failed for user {login_data.username}: {str(e)}")
            raise InvalidPasswordError(f"Authentication failed: {str(e)}")

    async def create_initial_users(self) -> list:
        """
        Create initial admin and regular users if they don't exist
        
        Returns:
            List of usernames created
        """
        try:
            return await self.initialization_service.create_initial_users()
        except Exception as e:
            logger.error(f"Failed to create initial users: {str(e)}")
            raise
