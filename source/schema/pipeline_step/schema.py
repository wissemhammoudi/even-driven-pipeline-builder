from pydantic import BaseModel, Field
from typing import Optional, Dict,List
from datetime import datetime


class StepBase(BaseModel):
    name: str
    description: Optional[str] = None
    step_config: Dict
    config_ids: List[int] = Field(default_factory=list)
    order: int

class PipelineStepCreate(StepBase):
    pipeline_id: int

class PipelineStepUpdate(BaseModel):
    step_id: int
    name: Optional[str] = None
    description: Optional[str] = None
    step_config: Optional[Dict] = None

class PipelineStepResponse(BaseModel):
    step_id: int
    name: str
    description: Optional[str] = None
    step_config: Dict
    config_ids: List[int]
    order: int
    pipeline_id: int
    
    class Config:
        from_attributes = True
