from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
import enum

class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"

class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr
    first_name: Optional[str] = None
    last_name:  Optional[str] = None
    role:      Optional[UserRole] = UserRole.user
    
    @field_validator('first_name', 'last_name', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v
    
    @field_validator('role', mode='before')
    @classmethod
    def validate_role(cls, v):
        if isinstance(v, str):
            if v == "admin":
                return UserRole.admin
            elif v == "user":
                return UserRole.user
            else:
                raise ValueError(f'Invalid role: {v}. Must be "user" or "admin"')
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @field_validator('password', mode='before')
    @classmethod
    def validate_password(cls, v):
        if not v or len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserResponse(BaseModel):
    user_id: str  
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    
    class Config:
        from_attributes = True  # This allows Pydantic to work with SQLAlchemy models

class PasswordUpdate(BaseModel):
    user_id: str  
    old_password: str
    new_password: str

class LoginSchema(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    user_id: str  
    username: str
    email: EmailStr = None
    first_name: str = None
    last_name: str = None    

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    role: Optional[UserRole] = None

class BulkUserDelete(BaseModel):
    user_ids: List[str]




