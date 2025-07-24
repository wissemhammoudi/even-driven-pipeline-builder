from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.schema import Identity
from source.repository.database import Base
from sqlalchemy.orm import relationship
class Step(Base):
    __tablename__ = "steps"

    step_id = Column(Integer, Identity(always=True), primary_key=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    step_config = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    is_deprecated = Column(Boolean, default=False, nullable=False)
    pipeline_id = Column(Integer, ForeignKey("pipelines.pipeline_id"), nullable=False)
    order = Column(Integer,nullable=False)
    pipeline = relationship("Pipeline", back_populates="steps")
    config_associations = relationship("StepConfigurationAssociation", back_populates="step", cascade="all, delete-orphan")
