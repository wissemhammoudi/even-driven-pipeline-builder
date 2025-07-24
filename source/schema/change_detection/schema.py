from pydantic import BaseModel
from typing import Any
from datetime import datetime
from typing import Literal
from enum import Enum


class SchemaChangeTypeEnum(str, Enum):
    breaking = "breaking"
    non_breaking = "non_breaking"


class SchemaChangeEventSchema(BaseModel):
    id: int
    pipeline_id: int
    event_time: datetime
    change_type: Literal['breaking', 'non_breaking']
    payload: str
    human_readable_message: str

    class Config:
        orm_mode = True 