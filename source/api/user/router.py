from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from source.schema.user.schemas import UserCreate, UserUpdate, UserResponse, PasswordUpdate, LoginSchema, BulkUserDelete
from source.service.user.services import UserService
from source.exceptions.exceptions import UserNotFoundError, DuplicateUserError, InvalidPasswordError
from source.config.config import api_config
from pydantic import ValidationError, BaseModel
from sqlalchemy.exc import IntegrityError
from source.service.user.services import UserService
from source.schema.user.schemas import UserRole     
from source.service.authentication.keycloak_auth import get_current_user, require_user_role, require_admin_role 

# Define paginated response model
class PaginatedUserResponse(BaseModel):
    users: List[UserResponse]
    total: int
    limit: int
    offset: int
    has_more: bool

user_router = APIRouter(prefix=f"{api_config.api_prefix}/users")

@user_router.post('/signup', status_code=status.HTTP_201_CREATED)
def signup(
    user_data: UserCreate,
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_admin_role)
):
    try:
        return user_service.signup(user_data)
    except DuplicateUserError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@user_router.post('/login')
async def login(login_data: LoginSchema, user_service: UserService = Depends(UserService)):
    try:
        return await user_service.login(login_data)
    except InvalidPasswordError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

@user_router.get('/', response_model=List[UserResponse])
def get_all_users(
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_admin_role)
):
    return user_service.get_all_users()

@user_router.get('/me', response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(require_user_role)):
    """Get current user information"""
    try:
        # Debug logging
        print(f"DEBUG: /me endpoint - current_user: {current_user}")
        print(f"DEBUG: /me endpoint - user_id: {current_user.get('user_id')}")
        print(f"DEBUG: /me endpoint - username: {current_user.get('username')}")
        
        user_service = UserService()
        user = user_service.get_user_by_id(current_user['user_id'])
        
        print(f"DEBUG: /me endpoint - user from database: {user}")
        
        if user:
            return user
        else:
            print(f"DEBUG: /me endpoint - User not found in database for ID: {current_user['user_id']}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except Exception as e:
        print(f"DEBUG: /me endpoint - Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@user_router.post('/debug/create-admin')
async def debug_create_admin():
    """Temporary endpoint to manually create admin user in local database"""
    try:
        from source.models.user.models import User
        from source.schema.user.schemas import UserRole
        
        user_service = UserService()
        
        # Check if admin user already exists by username
        existing_user = user_service.user_repository.get_user_by_username('admin123')
        if existing_user:
            return {"message": "Admin user already exists", "user": existing_user}
        
        # Check if admin user exists by email
        existing_user_by_email = user_service.user_repository.get_user_by_email('admin@example.com')
        if existing_user_by_email:
            return {"message": "Admin user already exists with this email", "user": existing_user_by_email}
        
        # Create admin user directly in local database
        admin_user = User(
            user_id='de02fb54-beec-4f90-8401-a3deb5979bad',  # From logs
            username='admin123',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            role=UserRole.admin
        )
        
        created_user = user_service.user_repository.create_user(admin_user)
        return {"message": "Admin user created successfully", "user": created_user}
        
    except Exception as e:
        print(f"DEBUG: Error creating admin user: {e}")
        print(f"DEBUG: Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@user_router.get('/debug/health')
async def debug_health_check():
    """Health check endpoint to verify database connectivity"""
    try:
        user_service = UserService()
        
        # Try to get user count
        all_users = user_service.user_repository.get_all_active_user()
        user_count = len(all_users) if all_users else 0
        
        return {
            "status": "healthy",
            "database": "connected",
            "user_count": user_count,
            "message": "Database connection successful"
        }
        
    except Exception as e:
        print(f"DEBUG: Health check failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "message": "Database connection failed"
        }

@user_router.get('/{username}', response_model=UserResponse)
def get_user_by_username(
    username: str, 
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_user_role)
):
    try:
        return user_service.get_user_by_username(username)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
@user_router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,  
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_admin_role)
):
    try:
        user_service.delete_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
@user_router.patch('/password')
def update_password(
    password_data: PasswordUpdate, 
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_user_role)
):
    try:
        return user_service.update_password(password_data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidPasswordError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
@user_router.patch('/', response_model=UserResponse)
async def update_user(
    user_data: UserUpdate, 
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_user_role)
):
    try:
        await user_service.update_user(user_data)
        
        # Return the updated user object
        updated_user = user_service.get_user_by_id(user_data.user_id)
        if updated_user:
            return updated_user
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User updated but failed to retrieve updated user data"
            )
            
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateUserError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

# Admin-only endpoints
@user_router.post('/admin/create', response_model=UserResponse)
async def create_user_admin(
    user_data: UserCreate,
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_admin_role)
):
    """Admin endpoint to create new users"""
    try:
        # Debug logging
        print(f"DEBUG: Received user data: {user_data}")
        print(f"DEBUG: User data type: {type(user_data)}")
        print(f"DEBUG: Role value: {user_data.role}")
        print(f"DEBUG: Role type: {type(user_data.role)}")
        
        # Create the user
        result = await user_service.signup(user_data)
        
        # Get the created user to return the full user object
        if result and 'user_id' in result:
            created_user = user_service.get_user_by_id(result['user_id'])
            if created_user:
                return created_user
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                    detail="User created but failed to retrieve user data"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Failed to create user"
            )
            
    except DuplicateUserError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        print(f"DEBUG: Error creating user: {e}")
        print(f"DEBUG: Error type: {type(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@user_router.get('/admin/all', response_model=PaginatedUserResponse)
def get_all_users_admin(
    search: str = None,
    role: str = None,
    limit: int = 100,
    offset: int = 0,
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_admin_role)
):
    """Admin endpoint to get all users with filtering and pagination"""
    return user_service.get_all_users_filtered(search=search, role=role, limit=limit, offset=offset)

@user_router.post('/admin/bulk-delete', status_code=status.HTTP_204_NO_CONTENT)
async def bulk_delete_users(
    bulk_data: BulkUserDelete,
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_admin_role)
):
    """Admin endpoint to delete multiple users"""
    try:
        for user_id in bulk_data.user_ids:
            await user_service.delete_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@user_router.get('/admin/{user_id}', response_model=UserResponse)
def get_user_by_id_admin(
    user_id: str,
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_admin_role)
):
    """Admin endpoint to get user by ID"""
    try:
        return user_service.get_user_by_id(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@user_router.patch('/admin/{user_id}', response_model=UserResponse)
async def update_user_admin(
    user_id: str,
    user_data: UserUpdate,
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_admin_role)
):
    """Admin endpoint to update any user"""
    try:
        # Ensure the user_id in the path matches the user_data
        user_data.user_id = user_id
        await user_service.update_user(user_data)
        
        # Return the updated user object
        updated_user = user_service.get_user_by_id(user_id)
        if updated_user:
            return updated_user
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User updated but failed to retrieve updated user data"
            )
            
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateUserError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@user_router.delete('/admin/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_admin(
    user_id: str,
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_admin_role)
):
    """Admin endpoint to delete any user"""
    try:
        await user_service.delete_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
