from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, List
import enum

class UserRole(str, enum.Enum):
    """User roles in the system"""
    user = "user"
    admin = "admin"

class UserBase(BaseModel):
    """Base user model with common fields"""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User's email address")
    first_name: Optional[str] = Field(None, max_length=50, description="User's first name")
    last_name: Optional[str] = Field(None, max_length=50, description="User's last name")
    role: Optional[UserRole] = Field(UserRole.user, description="User role in the system")
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    @field_validator('first_name', 'last_name', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        """Convert empty strings to None for optional fields"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v
    
    @field_validator('role', mode='before')
    @classmethod
    def validate_role(cls, v):
        """Validate and normalize user role"""
        if isinstance(v, str):
            v = v.lower().strip()
            if v == "admin":
                return UserRole.admin
            elif v == "user":
                return UserRole.user
            else:
                raise ValueError(f'Invalid role: {v}. Must be "user" or "admin"')
        return v

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    
    @field_validator('password', mode='before')
    @classmethod
    def validate_password(cls, v):
        """Validate password requirements"""
        if not v or len(v.strip()) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v.strip()

class UserResponse(BaseModel):
    """Schema for user response data"""
    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="User's username")
    email: str = Field(..., description="User's email address")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    role: Optional[UserRole] = Field(None, description="User role in the system")
    
    model_config = ConfigDict(
        from_attributes=True,  # This allows Pydantic to work with SQLAlchemy models
        str_strip_whitespace=True
    )

class PasswordUpdate(BaseModel):
    """Schema for password update requests"""
    user_id: str = Field(..., description="User ID for password update")
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    
    @field_validator('new_password', mode='before')
    @classmethod
    def validate_new_password(cls, v):
        """Validate new password requirements"""
        if not v or len(v.strip()) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v.strip()

class LoginSchema(BaseModel):
    """Schema for user login"""
    username: str = Field(..., description="Username for login")
    password: str = Field(..., description="Password for login")
    
    model_config = ConfigDict(
        str_strip_whitespace=True
    )

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    user_id: str = Field(..., description="User ID to update")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="New username")
    email: Optional[EmailStr] = Field(None, description="New email address")
    first_name: Optional[str] = Field(None, max_length=50, description="New first name")
    last_name: Optional[str] = Field(None, max_length=50, description="New last name")
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    @field_validator('username', 'first_name', 'last_name', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        """Convert empty strings to None for optional fields"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

class Token(BaseModel):
    """Schema for authentication tokens"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type (usually 'Bearer')")

class TokenData(BaseModel):
    """Schema for token payload data"""
    username: str = Field(..., description="Username from token")
    email: str = Field(..., description="Email from token")
    first_name: Optional[str] = Field(None, description="First name from token")
    last_name: Optional[str] = Field(None, description="Last name from token")
    role: Optional[UserRole] = Field(None, description="User role from token")

class BulkUserDelete(BaseModel):
    """Schema for bulk user deletion"""
    user_ids: List[str] = Field(..., min_items=1, max_items=100, description="List of user IDs to delete")
    
    @field_validator('user_ids')
    @classmethod
    def validate_user_ids(cls, v):
        """Validate that user IDs are not empty"""
        if not v or any(not uid.strip() for uid in v):
            raise ValueError('User IDs cannot be empty')
        return [uid.strip() for uid in v]

class PaginatedUserResponse(BaseModel):
    """Schema for paginated user responses"""
    users: List[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., ge=0, description="Total number of users")
    limit: int = Field(..., ge=1, le=1000, description="Number of users per page")
    offset: int = Field(..., ge=0, description="Number of users skipped")
    has_more: bool = Field(..., description="Whether there are more users available")
    
    @field_validator('total', 'limit', 'offset')
    @classmethod
    def validate_pagination(cls, v, info):
        """Validate pagination parameters"""
        if info.field_name == 'total' and v < 0:
            raise ValueError('Total count cannot be negative')
        elif info.field_name == 'limit' and (v < 1 or v > 1000):
            raise ValueError('Limit must be between 1 and 1000')
        elif info.field_name == 'offset' and v < 0:
            raise ValueError('Offset cannot be negative')
        return v
