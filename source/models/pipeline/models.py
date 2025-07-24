
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SqlEnum
import enum
from sqlalchemy.schema import Identity
from source.repository.database import Base
from sqlalchemy.orm import relationship
from source.models.user_pipeline_access.model import UserPipelineAccess
from source.schema.pipeline.schema import PipelineStatusEnum


class Pipeline(Base):
    __tablename__ = "pipelines"

    pipeline_id = Column(Integer, Identity(always=True), primary_key=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    is_deprecated = Column(Boolean, default=False, nullable=False)
    created_by = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    status = Column(SqlEnum(PipelineStatusEnum), default=PipelineStatusEnum.stopped, nullable=False)

    owner = relationship("User", back_populates="pipelines")
    steps = relationship("Step", back_populates="pipeline")
    pipeline_runs = relationship("PipelineRun", back_populates="pipeline", cascade="all, delete-orphan")
    user_pipeline_accesses = relationship("UserPipelineAccess", back_populates="pipeline")
    dashboard_associations = relationship("DashboardPipelineAssociation", back_populates="pipeline")
