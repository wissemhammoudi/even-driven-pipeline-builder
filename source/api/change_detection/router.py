from fastapi import APIRouter
from typing import List, Optional
from source.service.change_detection.service import ChangeDetectionService
from source.schema.change_detection.schema import SchemaChangeEventSchema

schema_change_detection_router = APIRouter(prefix="/change-detection")


@schema_change_detection_router.get("/schema-changes/pipeline/{pipeline_id}", response_model=List[SchemaChangeEventSchema])
async def get_schema_changes_by_pipeline(pipeline_id: int):

    service = ChangeDetectionService()
    events = service.get_schema_changes_by_pipeline(pipeline_id)
    return events

@schema_change_detection_router.get("/schema-changes/pipeline/{pipeline_id}/breaking", response_model=List[SchemaChangeEventSchema])
async def get_breaking_changes_by_pipeline(pipeline_id: int):
    service = ChangeDetectionService()
    events = service.get_breaking_changes_by_pipeline(pipeline_id)
    return events 
