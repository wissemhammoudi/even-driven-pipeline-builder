from fastapi import APIRouter, Query
from typing import List, Optional
from source.service.change_detection.service import ChangeDetectionService
from source.schema.change_detection.schema import SchemaChangeEventSchema

schema_change_detection_router = APIRouter(prefix="/change-detection")

@schema_change_detection_router.get("/schema-changes/detect")
async def detect_schema_changes(pipeline_id: Optional[int] = Query(None)):
    """
    Detect schema changes for a specific pipeline or all pipelines
    """
    service = ChangeDetectionService()
    
    if pipeline_id:
        events = service.get_schema_changes_by_pipeline(pipeline_id)
        return {
            "pipeline_id": pipeline_id,
            "events": events,
            "total_changes": len(events)
        }
    else:
        all_events = service.get_all_schema_changes()
        return {
            "events": all_events,
            "total_changes": len(all_events)
        }

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