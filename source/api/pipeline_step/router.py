from fastapi import APIRouter, status, HTTPException, Depends
from source.schema.pipeline_step.schema import PipelineStepCreate, PipelineStepUpdate
from source.service.pipeline_step.service import PipelineStepService
from source.exceptions.exceptions import StepNotFoundError
from source.config.config import api_config
from source.service.authentication.keycloak_auth import require_admin_role, require_user_role

step_router = APIRouter(prefix=f"{api_config.api_prefix}/steps")

@step_router.post("/", status_code=status.HTTP_201_CREATED)
def create_step(
    data: PipelineStepCreate, 
    step_service: PipelineStepService = Depends(PipelineStepService),
    current_user: dict = Depends(require_admin_role)
):
    try:
        return step_service.create_step(data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@step_router.patch("/", status_code=status.HTTP_200_OK)
def update_step(
    data: PipelineStepUpdate,
    step_service: PipelineStepService = Depends(PipelineStepService),
    current_user: dict = Depends(require_admin_role)
):
    try:
        return step_service.update_step(data)
    except StepNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@step_router.delete("/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_step(
    step_id: int,
    step_service: PipelineStepService = Depends(PipelineStepService),
    current_user: dict = Depends(require_admin_role)
):
    try:
        step_service.delete_step(step_id)
        return {"message": "Step soft-deleted successfully."}
    except StepNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@step_router.get("/step/{pipeline_id}")
def list_pipelines_by_pipeline(
    pipeline_id: int,
    step_service: PipelineStepService = Depends(PipelineStepService),
    current_user: dict = Depends(require_user_role)
):
    try:
        return step_service.get_steps_by_pipeline(pipeline_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))