from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class DashboardStats(BaseModel):
    pipelines: Dict[str, int]
    runs: Dict[str, Any]

class RecentRun(BaseModel):
    run_id: int
    pipeline_id: int
    pipeline_name: str
    status: str
    duration_minutes: float
    created_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    created_by: int

class RecentPipeline(BaseModel):
    pipeline_id: int
    name: str
    description: Optional[str]
    status: str
    created_at: Optional[str]
    created_by: int
    step_count: int

class DailyRunStats(BaseModel):
    date: str
    total_runs: int
    successful_runs: int
    failed_runs: int
    success_rate: float
    avg_duration: float

class PipelinePerformance(BaseModel):
    pipeline_id: int
    name: str
    total_runs: int
    successful_runs: int
    success_rate: float

class AnalyticsData(BaseModel):
    daily_runs: List[DailyRunStats]
    pipeline_status: Dict[str, int]
    top_performing_pipelines: List[PipelinePerformance]

class DashboardData(BaseModel):
    stats: DashboardStats
    recent_runs: List[RecentRun]
    analytics: AnalyticsData
    recent_pipelines: List[RecentPipeline]
    generated_at: str

class DashboardResponse(BaseModel):
    success: bool
    data: DashboardData
    message: Optional[str] = None 