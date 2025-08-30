from fastapi import APIRouter, HTTPException, Depends
from source.schema.agentic_transformation.schema import TransformationRequest
from source.config.config import api_config
from source.service.authentication.keycloak_auth import require_admin_role
from source.service.PipelineManager.transformationAgent import send_transformation_request

router_transformation = APIRouter(prefix=f"{api_config.api_prefix}/transformation")


@router_transformation.post("/create-transformation")
async def create_transformation(
    request: TransformationRequest,
    current_user: dict = Depends(require_admin_role)
):
    try:
        transformation_data = request.dict()
        result = await send_transformation_request(transformation_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
