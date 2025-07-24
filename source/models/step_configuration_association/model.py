from sqlalchemy import Column, ForeignKey, Integer
from source.repository.database import Base
from sqlalchemy.orm import relationship

class StepConfigurationAssociation(Base):
    __tablename__ = "step_configuration_association"

    step_id = Column(Integer, ForeignKey("steps.step_id"), primary_key=True)
    step_config_id = Column(Integer, ForeignKey("configurations.step_config_id"), primary_key=True)

    step = relationship("Step", back_populates="config_associations")
    step_config = relationship("configuration", back_populates="step_associations")
