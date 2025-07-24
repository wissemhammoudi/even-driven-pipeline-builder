import enum
from pydantic import BaseModel
from typing import List
from datetime import datetime


class GrantType(enum.Enum):
    OWNER = "OWNER"
    VIEW = "VIEW"


class UserPipelineAccessBase(BaseModel):
    user_id: int
    pipeline_id: int
    grant_type: GrantType
    granted_by: int


class UserPipelineAccessCreate(UserPipelineAccessBase):
    pass


class UserPipelineAccessUpdate(BaseModel):
    user_id: int
    pipeline_id: int
    grant_type: GrantType
    granted_by: int


class UserPipelineAccessResponse(UserPipelineAccessBase):
    granted_at: datetime

    class Config:
        from_attributes = True


class BulkAccessGrant(BaseModel):
    pipeline_id: int
    user_ids: List[int]
    grant_type: GrantType      
    granted_by: int


class BulkAccessRevoke(BaseModel):
    pipeline_id: int
    user_ids: List[int]


class AccessSummary(BaseModel):
    pipeline_id: int
    total_users: int
    views: List[dict]
    accesses: List[dict]


class BulkOperationResult(BaseModel):
    success_count: int
    failure_count: int
    total_processed: int