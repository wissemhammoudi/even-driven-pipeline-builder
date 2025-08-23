from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from source.repository.database import Base
from source.schema.user.schemas import UserRole

class User(Base):

    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, nullable=False, comment="Keycloak user ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="Unique username")
    email = Column(String(120), unique=True, nullable=False, index=True, comment="User's email address")
    first_name = Column(String(50), nullable=True, comment="User's first name")
    last_name = Column(String(50), nullable=True, comment="User's last name")
    role = Column(Enum(UserRole, name="user_role"), default=UserRole.user, nullable=False, comment="User role in the system")
    is_deleted = Column(Boolean, default=False, nullable=False, comment="Soft delete flag")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="User creation timestamp")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="Last update timestamp")

    pipelines = relationship("Pipeline", back_populates="owner", cascade="all, delete-orphan")
    pipeline_runs = relationship("PipelineRun", back_populates="creator", cascade="all, delete-orphan")
    user_pipeline_accesses = relationship("UserPipelineAccess", foreign_keys="[UserPipelineAccess.user_id]", back_populates="user")
    user_superset_accounts = relationship("UserSupersetAccountAssociation", back_populates="user")

    def __repr__(self):
        """String representation of the User model"""
        return f"<User(id='{self.user_id}', username='{self.username}', email='{self.email}', role='{self.role}')>"

    def __str__(self):
        """Human-readable string representation"""
        return f"User {self.username} ({self.email}) - {self.role.value}"

    @property
    def full_name(self) -> str:
        """Get the user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username

    @property
    def is_active(self) -> bool:
        """Check if the user is active (not deleted)"""
        return not self.is_deleted

    @property
    def is_admin(self) -> bool:
        """Check if the user has admin role"""
        return self.role == UserRole.admin

    def to_dict(self) -> dict:
        """Convert user to dictionary representation"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role.value if self.role else None,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

