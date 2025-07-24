from fastapi import APIRouter, Depends
from source.schema.pipeline_run.schema import PipelineRunCreate
from source.service.pipeline_run.service import PipelineRunService
from source.config.config import settings
pipeline_run_router = APIRouter(prefix=f"{settings.api_prefix}/pipeline-runs")


@pipeline_run_router.get("/pipeline/{pipeline_id}")
def get_pipeline_runs_by_pipeline_id(
    pipeline_id: int,
    PipelineRunService: PipelineRunService = Depends(PipelineRunService),
):
    runs = PipelineRunService.get_pipeline_runs_by_pipeline_id(pipeline_id)
    return runs

@pipeline_run_router.post("/start")
def start_pipeline(
    run: PipelineRunCreate,
    PipelineRunService: PipelineRunService = Depends(PipelineRunService),
):
    return PipelineRunService.start_pipeline(run)
