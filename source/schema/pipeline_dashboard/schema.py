from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class DurationDistributionResponse(BaseModel):
    duration_range: str
    success_count: int
    failure_count: int
    run_count: int

class RunStatusDistributionResponse(BaseModel):
    status: str
    count: int

class PipelineRunVolumeResponse(BaseModel):
    date: Optional[str]
    total_runs: int

class RunSuccessFailureTrendResponse(BaseModel):
    date: str
    successful_runs: int
    failed_runs: int

class PipelineInfoResponse(BaseModel):
    pipeline_id: int
    name: str
    description: Optional[str]
    step_count: int
    created_at: Optional[str]
    is_deprecated: bool

class PipelineStatsResponse(BaseModel):
    total_runs: int
    successful_runs: int
    failed_runs: int
    success_rate: float
    avg_duration_minutes: float
    avg_duration_seconds: float
    avg_duration_milliseconds: float
    avg_duration_formatted: str
    individual_durations: List[Dict[str, Any]]

class PipelineAnalyticsChartsResponse(BaseModel):
    daily_runs: List[Dict[str, Any]]
    duration_distribution: List[Dict[str, Any]]
    success_failure_distribution: List[Dict[str, Any]]

class PipelineAnalyticsResponse(BaseModel):
    pipeline_info: PipelineInfoResponse
    stats: PipelineStatsResponse
    charts: PipelineAnalyticsChartsResponse
    days_filter: int
    generated_at: str

class ErrorResponse(BaseModel):
    error: str
    pipeline_info: Dict[str, Any] = {}
    stats: Dict[str, Any] = {}
    charts: Dict[str, Any] = {}
    days_filter: int
    generated_at: str 