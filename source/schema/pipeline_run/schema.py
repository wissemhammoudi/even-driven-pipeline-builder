from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class RunStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
  
class PipelineRunCreate(BaseModel):
    pipeline_id: int
    user_id:int

class PipelineRunRead(BaseModel):
    run_id: int
    pipeline_id: int
    start_time: datetime
    end_time: datetime | None
    status: RunStatus
    pipeline_run: str | None
    created_by: int
    is_deleted: bool

