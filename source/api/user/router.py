from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from source.schema.user.schemas import UserCreate, UserUpdate, UserResponse, PasswordUpdate, LoginSchema, BulkUserDelete, PaginatedUserResponse
from source.service.user.services import UserService
from source.exceptions.exceptions import UserNotFoundError, DuplicateUserError, InvalidPasswordError
from source.config.config import api_config
from source.service.authentication.keycloak_auth import require_user_role, require_admin_role


user_router = APIRouter(prefix=f"{api_config.api_prefix}/users")

@user_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_admin_role)
):
    try:
        return await user_service.signup(user_data)
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
    try:
        user_service = UserService()
        user = user_service.get_user_by_id(current_user['user_id'])
        
        if user:
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

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
async def delete_user(
    user_id: str,  
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_admin_role)
):
    try:
        await user_service.delete_user(user_id)
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
        user_data.user_id = current_user['user_id']
        
        await user_service.update_user(user_data)
        
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

@user_router.post('/admin/create', response_model=UserResponse)
async def create_user_admin(
    user_data: UserCreate,
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_admin_role)
):
    try:
        result = await user_service.signup(user_data)
        
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
    return user_service.get_all_users_filtered(search=search, role=role, limit=limit, offset=offset)

@user_router.post('/admin/bulk-delete', status_code=status.HTTP_204_NO_CONTENT)
async def bulk_delete_users(
    bulk_data: BulkUserDelete,
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_admin_role)
):
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
    try:
        user_data.user_id = user_id
        await user_service.update_user(user_data)
        
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
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@user_router.delete('/admin/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_admin(
    user_id: str,
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_admin_role)
):
    try:
        await user_service.delete_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
