from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from source.repository.user.repository import UserRepository
from source.models.user.models import User
from source.schema.user.schemas import TokenData

class AuthService:
    def __init__(self, user_repo: UserRepository, secret_key: str, algorithm: str, token_expiry_minutes: int):
        self.user_repo = user_repo
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expiry_minutes = token_expiry_minutes
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.user_repo.get_user_by_username(email)
        if not user or not self.verify_password(password, user.password_hash):
            return None
        return user

    def create_access_token(self, user: User) -> str:
        data = {
            "sub": user.email,
            "username": user.username,
            "user_id": user.user_id,
            "role": user.role,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
        expire = datetime.utcnow() + timedelta(minutes=self.token_expiry_minutes)
        data.update({"exp": expire})
        return jwt.encode(data, self.secret_key, algorithm=self.algorithm)

    def get_current_user(self, token: str) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            username: str = payload.get("username") 
            if email is None:
                raise credentials_exception
            token_data = TokenData(email=email, username=username)
        except JWTError:
            raise credentials_exception

        user = self.user_repo.get_by_email(token_data.email)
        if user is None:
            raise credentials_exception
        return user
