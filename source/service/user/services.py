from typing import Dict, Any, Optional
from source.repository.user.repository import UserRepository
from source.schema.user.schemas import UserCreate, UserUpdate, UserResponse, PasswordUpdate, LoginSchema, UserRole
from source.exceptions.exceptions import UserNotFoundError, DuplicateUserError, InvalidPasswordError
from source.models.user.models import User
from source.service.authentication.keycloak_auth import keycloak_auth_service
from .superset_service import UserSupersetService
from .initialization_service import UserInitializationService
from datetime import datetime, timezone

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        self._keycloak_service = None
        self.superset_service = UserSupersetService()
        self.initialization_service = UserInitializationService()
    
    async def _get_keycloak_service(self):
        if self._keycloak_service is None:
            from .keycloak_service import UserKeycloakService
            self._keycloak_service = UserKeycloakService()
        return self._keycloak_service
    
    async def signup(self, user_data: UserCreate) -> Dict[str, Any]:
        try:
            existing_user = self.user_repository.get_user_by_email_and_username(
                user_data.email, user_data.username
            )
            if existing_user:
                raise DuplicateUserError("Username or email already exists")
            
            keycloak_service = await self._get_keycloak_service()
            keycloak_user_id = await keycloak_service.create_user(user_data)
            if not keycloak_user_id:
                raise Exception("Failed to create user in Keycloak")
            
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
            saved_user =  self.user_repository.get_user_by_id(keycloak_user_id)
            if not saved_user:
                raise Exception("User was not properly saved to database")
            
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
                else:
                    raise Exception(f"Failed to create user {user_data.username} in Superset")
                    
            except Exception as e:
                raise Exception(f"Failed to create Superset user for {user_data.username}: {str(e)}")
            
            return {
                "message": "User created successfully in Keycloak and local database",
                "user_id": keycloak_user_id,
                "username": user_data.username,
                "email": user_data.email
            }
            
        except DuplicateUserError:
            raise
        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")

    def get_all_users(self) -> list:
        try:
            users = self.user_repository.get_all_active_user()
            return users
        except Exception as e:
            raise Exception(f"Failed to get all users: {str(e)}")
    
    def get_all_users_filtered(self, search: str = None, role: str = None, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
       
        try:
            if limit <= 0 or limit > 1000:
                limit = 100
            if offset < 0:
                offset = 0
                
            result = self.user_repository.get_all_users_filtered(
                search=search, role=role, limit=limit, offset=offset
            )
            
            transformed_result = {
                "users": result.get('users', []),
                "total": result.get('total_count', 0),
                "limit": result.get('limit', limit),
                "offset": result.get('offset', offset),
                "has_more": (result.get('offset', 0) + result.get('limit', limit)) < result.get('total_count', 0)  # Add has_more field
            }
            
            return transformed_result
        except Exception as e:
            raise Exception(f"Failed to get filtered users: {str(e)}")
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
       
        try:
            user = self.user_repository.get_user_by_id(user_id)
            if user:
                return user
            else:
                raise UserNotFoundError(f"User with ID {user_id} not found")
        except Exception as e:
            raise Exception(f"Failed to get user by ID {user_id}: {str(e)}")
    
    def get_user_by_username(self, username: str) -> User:

        try:
            if not username:
                raise ValueError("Username cannot be empty")
                
            user = self.user_repository.get_active_user_by_username(username)
            if not user:
                raise UserNotFoundError(f"User with username '{username}' not found")
            return user
        except UserNotFoundError:
            raise Exception(f"Failed to get user by username {username}: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to get user by username {username}: {str(e)}")

    async def delete_user(self, user_id: str) -> Dict[str, str]:

        try:
            user = self.user_repository.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"User with ID {user_id} not found")

            keycloak_service = await self._get_keycloak_service()
            await keycloak_service.delete_user(user_id)
            
            self.user_repository.mark_deleted(user)
            
            return {"message": "User deleted successfully from Keycloak and local database"}
            
        except UserNotFoundError:
            raise
        except Exception as e:
            raise Exception(f"Failed to delete user: {str(e)}")

    def update_password(self, password_data: PasswordUpdate) -> None:

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
            raise Exception(f"Failed to update password for user {password_data.user_id}: {str(e)}")

    async def update_user(self, user_data: UserUpdate) -> Dict[str, str]:

        try:
            if not user_data.user_id:
                raise ValueError("User ID cannot be empty")
                
            user = self.user_repository.get_user_by_id(user_data.user_id)
            if not user:
                raise UserNotFoundError(f"User with ID {user_data.user_id} not found")
            
            if user_data.email:
                if '@' not in user_data.email or '.' not in user_data.email:
                    raise ValueError("Invalid email format")
                
                existing_email = self.user_repository.get_user_by_email(user_data.email)
                if existing_email and existing_email.user_id != user.user_id:
                    raise DuplicateUserError("Email already exists")
            
            if user_data.username:
                existing_username = self.user_repository.get_user_by_username(user_data.username)
                if existing_username and existing_username.user_id != user.user_id:
                    raise DuplicateUserError("Username already exists")
            
            keycloak_service = await self._get_keycloak_service()
            
            keycloak_success = await keycloak_service.update_user(user_data)
            
            if not keycloak_success:
                raise Exception("Failed to update user in Keycloak")
            
            update_data = {}
            if user_data.email:
                update_data['email'] = user_data.email
            if user_data.username:
                update_data['username'] = user_data.username
            if user_data.first_name:
                update_data['first_name'] = user_data.first_name
            if user_data.last_name:
                update_data['last_name'] = user_data.last_name
            if user_data.role:
                update_data['role'] = user_data.role
            
            if update_data:
                updated_user = self.user_repository.update_user(user_data.user_id, **update_data)
                if not updated_user:
                    raise Exception("Failed to update user in local database")
            
            return {"message": "User information updated successfully in Keycloak and local database"}
            
        except (UserNotFoundError, DuplicateUserError):
            raise
        except Exception as e:
            raise Exception(f"Failed to update user: {str(e)}")

    async def login(self, login_data: LoginSchema) -> Dict[str, Any]:
        try:
            
            if not login_data.username or not login_data.password:
                raise InvalidPasswordError("Username and password are required")
                
            keycloak_service = await self._get_keycloak_service()
            auth_result = await keycloak_service.authenticate_user(
                login_data.username, 
                login_data.password
            )
            
            if not auth_result:
                raise InvalidPasswordError("Invalid username or password")  
            
            user = self.user_repository.get_active_user_by_username(login_data.username)
            if not user:
                raise InvalidPasswordError("User account not found")
            
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
            raise InvalidPasswordError(f"Authentication failed: {str(e)}")

    async def create_initial_users(self) -> list:

        try:
            created_users = await self.initialization_service.create_initial_users()
            return created_users
        except Exception as e:
            raise Exception(f"Failed to create initial users: {str(e)}")
