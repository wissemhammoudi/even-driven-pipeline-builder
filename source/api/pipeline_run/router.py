from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from source.schema.pipeline_run.schema import PipelineRunCreate, PipelineRunUpdate, PipelineRunResponse
from source.service.pipeline_run.service import PipelineRunService
from source.exceptions.exceptions import PipelineRunNotFoundError
from source.config.config import api_config
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from source.service.user.services import UserService
from source.schema.user.schemas import UserRole     
from source.service.authentication.keycloak_auth import get_current_user, require_user_role, require_admin_role 

pipeline_run_router = APIRouter(prefix=f"{api_config.api_prefix}/pipeline-runs")


@pipeline_run_router.get("/pipeline/{pipeline_id}")
def get_pipeline_runs_by_pipeline_id(
    pipeline_id: int,
    PipelineRunService: PipelineRunService = Depends(PipelineRunService),
    current_user: dict = Depends(require_user_role)
):
    runs = PipelineRunService.get_pipeline_runs_by_pipeline_id(pipeline_id)
    return runs

@pipeline_run_router.post("/start")
def start_pipeline(
    run: PipelineRunCreate,
    PipelineRunService: PipelineRunService = Depends(PipelineRunService),
    current_user: dict = Depends(require_user_role)
):
    return PipelineRunService.start_pipeline(run)
