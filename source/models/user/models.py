from sqlalchemy import Column, String, DateTime, Identity,Integer,Boolean
from datetime import datetime
from source.repository.database import Base
from passlib.context import CryptContext
from source.schema.user.schemas import UserRole
from sqlalchemy import Enum
from sqlalchemy.orm import relationship
from source.models.user_pipeline_access.model import UserPipelineAccess

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    user_id       = Column(Integer,Identity(always=True),primary_key=True,nullable=False)
    username      = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    email         = Column(String(120), unique=True, nullable=False)
    first_name    = Column(String(50), nullable=True)
    last_name     = Column(String(50), nullable=True)
    role          = Column(Enum(UserRole, name="user_role"), default=UserRole.user, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at    = Column(DateTime, default=datetime.now, nullable=False)
    updated_at    = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    pipelines = relationship("Pipeline", back_populates="owner")
    pipeline_runs = relationship("PipelineRun", back_populates="creator", cascade="all, delete-orphan")
    user_pipeline_accesses = relationship("UserPipelineAccess", foreign_keys="[UserPipelineAccess.user_id]", back_populates="user")

