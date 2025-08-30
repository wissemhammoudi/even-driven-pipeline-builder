from fastapi import APIRouter, HTTPException, Depends
from source.schema.superset.schema import VisualizationControl
from source.config.config import api_config, superset_config
from source.service.user.services import UserService
from source.service.pipeline_step.service import PipelineStepService
from source.service.authentication.keycloak_auth import require_user_role

superset_router = APIRouter(prefix=f"{api_config.api_prefix}/superset")


@superset_router.post("/visualization/start")
def start_visualization(
    control: VisualizationControl,
    step_service: PipelineStepService = Depends(PipelineStepService),
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_user_role)
):
    """Start the visualization for a pipeline"""
    try:
        steps_data = step_service.get_steps_by_pipeline(control.pipeline_id)
        user = user_service.get_user_by_id(control.user_id)

        username = user.username
        password = user.username
        if not steps_data:
            raise HTTPException(status_code=404, detail="No steps found for this pipeline")
        return {
                "status": "started",
                "visualization_url": f"{superset_config.superset_user_url}",
                "username": username,
                "password": password,
            }

    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=500, detail=f"Failed to start visualization: {error_message}")
