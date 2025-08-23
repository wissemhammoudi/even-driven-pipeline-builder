from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from typing import Optional


class RunStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
  
class PipelineRunCreate(BaseModel):
    pipeline_id: int
    user_id: str 

class PipelineRunUpdate(BaseModel):
    end_time: Optional[datetime] = None
    status: Optional[RunStatus] = None
    pipeline_run: Optional[str] = None

class PipelineRunResponse(BaseModel):
    run_id: int
    pipeline_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    status: RunStatus
    pipeline_run: Optional[str] = None
    created_by: str 
    is_deleted: bool
    
    class Config:
        from_attributes = True

class PipelineRunRead(BaseModel):
    run_id: int
    pipeline_id: int
    start_time: datetime
    end_time: datetime | None
    status: RunStatus
    pipeline_run: str | None
    created_by: str  
    is_deleted: bool

