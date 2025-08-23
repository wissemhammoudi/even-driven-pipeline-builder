from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from source.schema.pipeline.schema import PipelineCreate, PipelineDelete, StepAdd, StepDelete, PipelineUpdate
from source.service.pipeline.service import PipelineService
from source.exceptions.exceptions import PipelineNotFoundError, StepIdNotFoundInPipeline
from source.config.config import api_config
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from source.schema.pipeline.schema import PostgreSQLMetadataRequest
from source.service.PipelineManager.sourceTablesMetadata import PostgreSQLSourceMetadata  
from datetime import datetime
from source.service.user.services import UserService
from source.schema.user.schemas import UserRole     
from source.service.authentication.keycloak_auth import get_current_user, require_user_role, require_admin_role 
pipeline_router = APIRouter(prefix=f"{api_config.api_prefix}/pipeline")

@pipeline_router.post("/schema")
def get_postgresql_schema_info(
    metadata_req: PostgreSQLMetadataRequest,
    current_user: dict = Depends(require_user_role)
):
    try:
        source = PostgreSQLSourceMetadata(
            host=metadata_req.host,
            dbname=metadata_req.dbname,
            user=metadata_req.user,
            password=metadata_req.password,
            port=metadata_req.port,
        )
        schema_info = source.get_schema_info(metadata_req.schema)
        return schema_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving schema info: {str(e)}"
        )

@pipeline_router.get("/")
def list_pipelines(
    user_id: str,  
    offset: int = 0, 
    limit: int = 10, 
    deprecated: bool = False, 
    name: str = None,
    created_date: str = None,
    PipelineService: PipelineService = Depends(PipelineService),
    UserService: UserService = Depends(UserService),
    current_user: dict = Depends(require_user_role)
    ):
    try:
        user = UserService.get_user_by_id(user_id)
        if not user:
                raise Exception(f"User with ID {user_id} not found")
        is_admin = user.role == UserRole.admin
        if is_admin:
            user_id = None
        return PipelineService.list_pipelines(
            user_id=user_id,
            offset=offset, 
            limit=limit, 
            deprecated=deprecated, 
            name=name,
            created_date=created_date
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@pipeline_router.get("/{pipeline_id}")
def get_pipeline_by_id(
    pipeline_id: int, 
    PipelineService: PipelineService = Depends(PipelineService),
    current_user: dict = Depends(require_user_role)
):
    try:
        return PipelineService.get_pipline_by_id(pipeline_id)
    except PipelineNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@pipeline_router.post("/",status_code=status.HTTP_201_CREATED)
def create_pipeline(
    pipeline_data: PipelineCreate, 
    pipeline_service: PipelineService = Depends(PipelineService),
    user_service: UserService = Depends(UserService),
    current_user: dict = Depends(require_admin_role)
):
    try:
        # Verify the user exists and has admin role
        user = user_service.get_user_by_id(pipeline_data.created_by)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {pipeline_data.created_by} not found"
            )
        
        if user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can create pipelines"
            )

        response, status_code = pipeline_service.create_pipeline(pipeline_data)
        if status_code == 201:
            return response
        else:
            raise HTTPException(
                status_code=status_code,
                detail=response.get("error", "Failed to create pipeline")
            )
        
    except ValidationError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Invalid input data", "errors": [{"field": err["loc"], "message": err["msg"]} for err in ve.errors()]}
        )    
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(ve)
        )
    except IntegrityError as ie:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": f"Data integrity violation: {str(ie)}"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@pipeline_router.delete("/{pipeline_id}", response_model=dict)
def delete_pipeline(
    pipeline_id: int, 
    PipelineService: PipelineService = Depends(PipelineService),
    current_user: dict = Depends(require_admin_role)
):
    try:
        PipelineService.delete_pipeline(PipelineDelete(pipeline_id=pipeline_id))
        return {"message": "Pipeline soft-deleted successfully."}
    except PipelineNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@pipeline_router.get("/{pipeline_id}/steps", response_model=List[int])
def get_pipeline_steps(
    pipeline_id: int, 
    PipelineService: PipelineService = Depends(PipelineService),
    current_user: dict = Depends(require_user_role)
):
    try:
        return PipelineService.get_pipeline_steps(pipeline_id)
    except PipelineNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@pipeline_router.get("/{pipeline_id}/steps/details")
def get_pipeline_steps_details(
    pipeline_id: int, 
    PipelineService: PipelineService = Depends(PipelineService),
    current_user: dict = Depends(require_user_role)
):
    try:
        return PipelineService.get_pipeline_steps_details(pipeline_id)
    except PipelineNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@pipeline_router.patch("/steps")
def add_step_to_pipeline(
    step_data: StepAdd, 
    PipelineService: PipelineService = Depends(PipelineService),
    current_user: dict = Depends(require_admin_role)
):
    try:
        return PipelineService.add_step_to_pipeline(step_data)
    except PipelineNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except StepIdNotFoundInPipeline as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@pipeline_router.delete("/steps")
def delete_steps_from_pipeline(
    step_data: StepDelete, 
    PipelineService: PipelineService = Depends(PipelineService),
    current_user: dict = Depends(require_admin_role)
):
    try:
        return PipelineService.delete_steps_from_pipeline(step_data)
    except PipelineNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except StepIdNotFoundInPipeline as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@pipeline_router.patch("/")
def update_pipeline(
    pipeline_data: PipelineUpdate,
    PipelineService: PipelineService = Depends(PipelineService),
    current_user: dict = Depends(require_admin_role)
):
    try:
        return PipelineService.update_pipeline(pipeline_data)
    except PipelineNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))