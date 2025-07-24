from fastapi import APIRouter, Depends, status, HTTPException
from source.schema.pipeline_step.schema import StepCreate,StepUpdate
from source.service.pipeline_step.service import StepService
from source.exceptions.exceptions import StepNotFoundError
from source.config.config import settings

step_router = APIRouter(prefix=f"{settings.api_prefix}/steps")

@step_router.post("/", status_code=status.HTTP_201_CREATED)
def create_step(
    data: StepCreate, 
    StepService: StepService = Depends(StepService)
):
    try:
        return StepService.create_step(data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@step_router.patch("/", status_code=status.HTTP_200_OK)
def update_step(data: StepUpdate,
                StepService: StepService = Depends(StepService)
                ):
    try:
        return StepService.update_step(data)
    except StepNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@step_router.delete("/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_step(step_id: int,
                StepService: StepService = Depends(StepService)
                ):
    try:
        StepService.delete_step(step_id)
        return {"message": "Step soft-deleted successfully."}
    except StepNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@step_router.get("/step/{pipeline_id}")
def list_pipelines_by_pipeline(pipeline_id: int,
                                StepService: StepService = Depends(StepService)
                               ):
    try:
        return StepService.get_steps_by_pipeline(pipeline_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))