from sqlalchemy import (
    Column,
    Integer,
    Enum,
    TIMESTAMP,
    ForeignKey,
    PrimaryKeyConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from source.repository.database import Base
from source.schema.user_pipeline_acess.schema import GrantType


class UserPipelineAccess(Base):

    __tablename__ = 'user_pipeline_access'

    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    pipeline_id = Column(Integer, ForeignKey('pipelines.pipeline_id'), nullable=False)
    grant_type = Column(Enum(GrantType, name="grant_type"), nullable=False)
    granted_by = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    granted_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'pipeline_id'),
    )

    user = relationship("User", foreign_keys=[user_id], back_populates="user_pipeline_accesses")
    pipeline = relationship("Pipeline", back_populates="user_pipeline_accesses")
