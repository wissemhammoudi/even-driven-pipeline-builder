import logging
from typing import Dict, Any, Optional
from source.repository.user.repository import UserRepository
from source.schema.user.schemas import UserCreate, UserUpdate, UserResponse, PasswordUpdate, LoginSchema, UserRole
from source.exceptions.exceptions import UserNotFoundError, DuplicateUserError, InvalidPasswordError
from source.models.user.models import User
from source.service.authentication.keycloak_auth import keycloak_auth_service
from .superset_service import UserSupersetService
from .initialization_service import UserInitializationService
from datetime import datetime, timezone


# Configure logging
logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        self._keycloak_service = None
        self.superset_service = UserSupersetService()
        self.initialization_service = UserInitializationService()
    
    async def _get_keycloak_service(self):
        """Get keycloak service instance when needed"""
        if self._keycloak_service is None:
            from .keycloak_service import UserKeycloakService
            self._keycloak_service = UserKeycloakService()
        return self._keycloak_service
    
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
            logger.info(f"=== Starting user creation for: {user_data.username} ===")
            
            # Check for existing user
            logger.info("Checking for existing user...")
            existing_user = self.user_repository.get_user_by_email_and_username(
                user_data.email, user_data.username
            )
            if existing_user:
                logger.warning(f"User creation failed: username or email already exists - {user_data.username}")
                raise DuplicateUserError("Username or email already exists")
            logger.info("✅ No existing user found")
            
            # Create user in Keycloak
            logger.info("Creating user in Keycloak...")
            keycloak_service = await self._get_keycloak_service()
            keycloak_user_id = await keycloak_service.create_user(user_data)
            if not keycloak_user_id:
                logger.error(f"Failed to create user {user_data.username} in Keycloak")
                raise Exception("Failed to create user in Keycloak")
            logger.info(f"✅ User created in Keycloak with ID: {keycloak_user_id}")
            
            # Create user in local database
            logger.info("Creating user in local database...")
            user = User(
                user_id=keycloak_user_id,  
                username=user_data.username,
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                role=user_data.role or UserRole.user,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            created_user = self.user_repository.create_user(user)
            logger.info(f"✅ User created in local database: {created_user.username}")
            
            # Verify user was saved to database
            logger.info("Verifying user was saved to database...")
            from source.repository.user.repository import UserRepository
            verify_repo = UserRepository()
            saved_user = verify_repo.get_user_by_id(keycloak_user_id)
            if saved_user:
                logger.info(f"✅ User verified in database: {saved_user.username} (ID: {saved_user.user_id})")
            else:
                logger.error(f"❌ User not found in database after creation: {keycloak_user_id}")
                raise Exception("User was not properly saved to database")
            
            # Create user in Superset (non-blocking)
            try:
                logger.info("Creating user in Superset...")
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
                    logger.info(f"✅ User {user_data.username} created in Superset with ID: {superset_user_id}")
                else:
                    logger.warning(f"⚠️ Failed to create user {user_data.username} in Superset")
                    
            except Exception as e:
                # Log the error but don't fail the user creation
                logger.error(f"Failed to create Superset user for {user_data.username}: {str(e)}")
            
            logger.info(f"=== User {user_data.username} created successfully with ID: {keycloak_user_id} ===")
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
            users = self.user_repository.get_all_active_user()
            logger.info(f"Retrieved {len(users)} active users")
            return users
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
                
            logger.info(f"Getting filtered users: search='{search}', role='{role}', limit={limit}, offset={offset}")
            result = self.user_repository.get_all_users_filtered(
                search=search, role=role, limit=limit, offset=offset
            )
            logger.info(f"Retrieved {len(result.get('users', []))} filtered users out of {result.get('total_count', 0)} total")
            
            # Transform the response to match PaginatedUserResponse schema
            transformed_result = {
                "users": result.get('users', []),
                "total": result.get('total_count', 0),  # Rename total_count to total
                "limit": result.get('limit', limit),
                "offset": result.get('offset', offset),
                "has_more": (result.get('offset', 0) + result.get('limit', limit)) < result.get('total_count', 0)  # Add has_more field
            }
            
            return transformed_result
        except Exception as e:
            logger.error(f"Failed to get filtered users: {str(e)}")
            raise

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            user = self.user_repository.get_user_by_id(user_id)
            if user:
                logger.info(f"Retrieved user by ID: {user_id}")
            else:
                logger.warning(f"User not found by ID: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {str(e)}")
            raise

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            user = self.user_repository.get_user_by_username(username)
            if user:
                logger.info(f"Retrieved user by username: {username}")
            else:
                logger.warning(f"User not found by username: {username}")
            return user
        except Exception as e:
            logger.error(f"Failed to get user by username {username}: {str(e)}")
            raise

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            user = self.user_repository.get_user_by_email(email)
            if user:
                logger.info(f"Retrieved user by email: {email}")
            else:
                logger.warning(f"User not found by email: {email}")
            return user
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {str(e)}")
            raise

    async def delete_user(self, user_id: str) -> Dict[str, str]:
        """
        Delete user from Keycloak and local database
        
        Args:
            user_id: ID of the user to delete
            
        Returns:
            Success message
            
        Raises:
            UserNotFoundError: If user not found
            Exception: If deletion fails
        """
        try:
            logger.info(f"🗑️ Starting user deletion process for user: {user_id}")
            
            # Check if user exists
            logger.info(f"🔍 Checking if user exists in database: {user_id}")
            user = self.user_repository.get_user_by_id(user_id)
            if not user:
                logger.warning(f"❌ User deletion failed: user not found - {user_id}")
                raise UserNotFoundError(f"User with ID {user_id} not found")
            
            logger.info(f"✅ User found in database: {user.username} (ID: {user.user_id})")
            
            # Delete from Keycloak first
            logger.info(f"🔑 Attempting to delete user from Keycloak: {user_id}")
            keycloak_service = await self._get_keycloak_service()
            keycloak_deleted = await keycloak_service.delete_user(user_id)
            if not keycloak_deleted:
                logger.warning(f"⚠️ Failed to delete user {user_id} from Keycloak")
            else:
                logger.info(f"✅ User {user_id} deleted from Keycloak successfully")
            
            # Mark as deleted in local database
            logger.info(f"💾 Marking user as deleted in local database: {user_id}")
            self.user_repository.mark_deleted(user_id)
            logger.info(f"✅ User {user_id} marked as deleted in local database")
            
            logger.info(f"🎉 User {user_id} deletion process completed successfully")
            return {"message": "User deleted successfully from Keycloak and local database"}
            
        except UserNotFoundError:
            logger.error(f"❌ UserNotFoundError during deletion: {user_id}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error during user deletion {user_id}: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            logger.error(f"❌ Error details: {str(e)}")
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
                logger.warning(f"Password update failed: user not found - {password_data.user_id}")
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
            logger.info(f"Updating user: {user_data.user_id}")
            
            if not user_data.user_id:
                raise ValueError("User ID cannot be empty")
                
            user = self.user_repository.get_user_by_id(user_data.user_id)
            if not user:
                logger.warning(f"User update failed: user not found - {user_data.user_id}")
                raise UserNotFoundError(f"User with ID {user_data.user_id} not found")
            
            # Check for duplicate email
            if user_data.email:
                # Basic email validation
                if '@' not in user_data.email or '.' not in user_data.email:
                    raise ValueError("Invalid email format")
                
                existing_email = self.user_repository.get_user_by_email(user_data.email)
                if existing_email and existing_email.user_id != user.user_id:
                    logger.warning(f"User update failed: email already exists - {user_data.email}")
                    raise DuplicateUserError("Email already exists")
            
            # Check for duplicate username
            if user_data.username:
                existing_username = self.user_repository.get_user_by_username(user_data.username)
                if existing_username and existing_username.user_id != user.user_id:
                    logger.warning(f"User update failed: username already exists - {user_data.username}")
                    raise DuplicateUserError("Username already exists")
            
            # Update in Keycloak first
            keycloak_service = await self._get_keycloak_service()
            
            # Call the local UserKeycloakService with the UserUpdate object
            keycloak_success = await keycloak_service.update_user(user_data)
            
            if not keycloak_success:
                logger.warning(f"Keycloak update failed for user {user_data.user_id}")
            else:
                logger.info(f"Keycloak update successful for user {user_data.user_id}")
            
            # Update local database using the repository method
            update_data = {}
            if user_data.email:
                update_data['email'] = user_data.email
                logger.debug(f"Adding email to update: {user_data.email}")
            if user_data.username:
                update_data['username'] = user_data.username
                logger.debug(f"Adding username to update: {user_data.username}")
            if user_data.first_name:
                update_data['first_name'] = user_data.first_name
                logger.debug(f"Adding first_name to update: {user_data.first_name}")
            if user_data.last_name:
                update_data['last_name'] = user_data.last_name
                logger.debug(f"Adding last_name to update: {user_data.last_name}")
            if user_data.role:
                update_data['role'] = user_data.role
                logger.debug(f"Adding role to update: {user_data.role}")
            
            logger.info(f"Update data prepared: {update_data}")
            
            if update_data:
                updated_user = self.user_repository.update_user(user_data.user_id, **update_data)
                if not updated_user:
                    raise Exception("Failed to update user in local database")
            
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
            logger.info(f"Login attempt for user: {login_data.username}")
            
            if not login_data.username or not login_data.password:
                logger.warning(f"Login failed: missing credentials for user {login_data.username}")
                raise InvalidPasswordError("Username and password are required")
                
            # Authenticate with Keycloak
            auth_result = await keycloak_auth_service.authenticate_user(
                login_data.username, 
                login_data.password
            )
            
            if not auth_result:
                logger.warning(f"Login failed: invalid credentials for user {login_data.username}")
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
            logger.info("Creating initial users...")
            created_users = await self.initialization_service.create_initial_users()
            logger.info(f"Initial users created: {created_users}")
            return created_users
        except Exception as e:
            logger.error(f"Failed to create initial users: {str(e)}")
            raise

    async def refresh_user_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh user access token
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New token data or None if refresh fails
        """
        try:
            logger.info("Refreshing user token...")
            from source.service.keycloak_service import get_keycloak_service
            
            keycloak_service = await get_keycloak_service()
            new_tokens = await keycloak_service.refresh_token(refresh_token)
            
            if new_tokens:
                logger.info("User token refreshed successfully")
                return new_tokens
            else:
                logger.warning("Failed to refresh user token")
                return None
                
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return None

    def get_user_role(self, user_id: str) -> Optional[UserRole]:
        """
        Get user role from local database
        
        Args:
            user_id: User ID
            
        Returns:
            User role or None if user not found
        """
        try:
            user = self.user_repository.get_user_by_id(user_id)
            if user:
                return user.role
            return None
        except Exception as e:
            logger.error(f"Failed to get user role for {user_id}: {str(e)}")
            return None
