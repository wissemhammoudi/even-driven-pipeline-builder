from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy.schema import Identity
from source.repository.database import Base
from sqlalchemy.orm import relationship

class configuration(Base):
    __tablename__ = "configurations"

    step_config_id = Column(Integer, Identity(always=True), primary_key=True, nullable=False)
    type = Column(String(100), nullable=False)
    tool = Column(String(255), nullable=False)
    plugin_type = Column(String(255), nullable=False)
    plugin_name = Column(String(255), nullable=False)
    is_deprecated = Column(Boolean, default=False, nullable=False)
    config = Column(JSON, nullable=True)
    
    step_associations = relationship("StepConfigurationAssociation", back_populates="step_config", cascade="all, delete-orphan")
