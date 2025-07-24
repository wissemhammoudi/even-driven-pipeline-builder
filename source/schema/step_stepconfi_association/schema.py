# source/schemas/step_stepconfig_association.py
from pydantic import BaseModel
from typing import List, Optional

class StepConfigurationAssociationBase(BaseModel):
    step_id: int
    step_config_id: int

class StepConfigurationAssociationCreate(StepConfigurationAssociationBase):
    pass

