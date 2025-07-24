# src/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import enum

class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"

class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr
    first_name: Optional[str] = None
    last_name:  Optional[str] = None
    role:      Optional[str] ="user"

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: Optional[str]

class PasswordUpdate(BaseModel):
    user_id: int
    old_password: str
    new_password: str

class LoginSchema(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    user_id:int
    username:str
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
    role: Optional[str]




