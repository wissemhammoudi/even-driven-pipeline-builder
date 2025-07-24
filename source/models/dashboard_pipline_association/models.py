from sqlalchemy import (
    Column,
    Integer,
    TIMESTAMP,
    ForeignKey,
    Identity
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from source.repository.database import Base


class DashboardPipelineAssociation(Base):

    __tablename__ = 'dashboard_pipeline_association'

    id = Column(Integer, Identity(always=True), primary_key=True, nullable=False)
    pipeline_id = Column(Integer, ForeignKey('pipelines.pipeline_id'), nullable=False)
    dashboard_id = Column(Integer, nullable=False)
    granted_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)


    pipeline = relationship("Pipeline", back_populates="dashboard_associations")
