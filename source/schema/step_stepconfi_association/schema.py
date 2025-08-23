from pydantic import BaseModel
from typing import List, Optional

class StepConfigurationAssociationBase(BaseModel):
    step_id: int
    step_config_id: int

class StepConfigurationAssociationCreate(StepConfigurationAssociationBase):
    pass

class StepConfigurationAssociationUpdate(BaseModel):
    step_id: Optional[int] = None
    step_config_id: Optional[int] = None

class StepConfigurationAssociationResponse(StepConfigurationAssociationBase):
    id: int
    
    class Config:
        from_attributes = True

