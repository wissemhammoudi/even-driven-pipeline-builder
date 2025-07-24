from fastapi import APIRouter, HTTPException
from source.service.PipelineManager.transformationAgent import send_transformation_request
from source.schema.agentic_transformation.schema import TransformationRequest
from source.config.config import settings
router_transformation = APIRouter(prefix=f"/api/{settings.version}/transformation")


@router_transformation.post("/create-transformation")
def create_transformation(request: TransformationRequest):
    try:
        result = send_transformation_request(
            transformation=request.transformation,
            schema_name=request.schema_name,
            db_host=request.db_host,
            db_port=request.db_port,
            db_name=request.db_name,
            db_user=request.db_user,
            db_password=request.db_password,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
