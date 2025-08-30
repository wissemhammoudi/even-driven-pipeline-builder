from fastapi import APIRouter, Depends
from source.schema.pipeline_run.schema import PipelineRunCreate
from source.service.pipeline_run.service import PipelineRunService
from source.config.config import api_config
from source.service.authentication.keycloak_auth import require_user_role

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
