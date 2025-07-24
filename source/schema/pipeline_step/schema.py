from pydantic import BaseModel
from typing import Optional, Dict,List
from datetime import datetime


class StepBase(BaseModel):
    name: str
    description: Optional[str] = None
    step_config: Dict
    config_ids: List[int] = []
    order:int

class StepCreate(StepBase):
    pipeline_id: int

class StepUpdate(BaseModel):
    step_id: int
    name: Optional[str] = None
    description: Optional[str] = None
    step_config: Optional[Dict] = None
