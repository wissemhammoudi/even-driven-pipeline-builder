from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from source.schema.user.schemas import UserCreate, UserResponse, UserUpdate, PasswordUpdate, LoginSchema
from source.service.user.services import UserService
from source.exceptions.exceptions import UserNotFoundError, DuplicateUserError, InvalidPasswordError
from source.config.config import settings

user_router = APIRouter(prefix=f"{settings.api_prefix}/users")

@user_router.post('/signup', status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate,user_service: UserService = Depends(UserService)):
    try:
        return user_service.signup(user_data)
    except DuplicateUserError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@user_router.post('/login')
def login(login_data: LoginSchema, user_service: UserService = Depends(UserService)):
    try:
        return user_service.login(login_data)
    except InvalidPasswordError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

@user_router.get('/', response_model=List[UserResponse])
def get_all_users(user_service: UserService = Depends(UserService)):
    return user_service.get_all_users()

@user_router.get('/{username}', response_model=UserResponse)
def get_user_by_username(username: str, user_service: UserService = Depends(UserService)):
    try:
        return user_service.get_user_by_username(username)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
@user_router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, user_service: UserService = Depends(UserService)):
    try:
        user_service.delete_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
@user_router.patch('/password')
def update_password(password_data: PasswordUpdate, user_service: UserService = Depends(UserService)):
    try:
        return user_service.update_password(password_data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidPasswordError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
@user_router.patch('/')
def update_user(user_data: UserUpdate, user_service: UserService = Depends(UserService)):
    try:
        return user_service.update_user(user_data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateUserError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
