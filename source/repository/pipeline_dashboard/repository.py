from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy import func, case
from source.models.pipeline.models import Pipeline
from source.models.pipeline_run.model import PipelineRun
from source.repository.database import get_db

database = get_db()

class PipelineDashboardRepository:
    def __init__(self):
        self.db = database

    def _format_duration(self, seconds: float) -> str:
        if seconds <= 0:
            return "0m 0s"
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"

    def _create_duration_bins(self, success_durations: List[float], failure_durations: List[float]) -> List[Dict[str, Any]]:
        all_durations = success_durations + failure_durations
        if not all_durations:
            return []
        
        min_duration, max_duration = min(all_durations), max(all_durations)
        range_size = (max_duration - min_duration) / 4
        
        bins = []
        for i in range(4):
            bucket_min = min_duration + (i * range_size)
            bucket_max = min_duration + ((i + 1) * range_size)
            
            if i == 3:
                success_count = sum(1 for d in success_durations if bucket_min <= d <= bucket_max)
                failure_count = sum(1 for d in failure_durations if bucket_min <= d <= bucket_max)
            else:
                success_count = sum(1 for d in success_durations if bucket_min <= d < bucket_max)
                failure_count = sum(1 for d in failure_durations if bucket_min <= d < bucket_max)
            
            if bucket_max < 60:
                range_label = f"{bucket_min:.1f}-{bucket_max:.1f}s"
            elif bucket_min < 60:
                range_label = f"{bucket_min:.1f}s-{bucket_max/60:.1f}m"
            else:
                range_label = f"{bucket_min/60:.1f}-{bucket_max/60:.1f}m"
            
            bins.append({
                "range": range_label,
                "success_count": success_count,
                "failure_count": failure_count,
                "total_count": success_count + failure_count
            })
        
        return bins

    def get_pipeline_analytics(self, pipeline_id: int, days: int = 30) -> Dict[str, Any]:
        try:
            pipeline = self.db.query(Pipeline).filter(Pipeline.pipeline_id == pipeline_id).first()
            if not pipeline:
                return {"error": "Pipeline not found"}
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            stats = self.db.query(
                func.count(PipelineRun.run_id).label('total'),
                func.sum(case((PipelineRun.status == "SUCCESS", 1), else_=0)).label('successful'),
                func.sum(case((PipelineRun.status == "FAILED", 1), else_=0)).label('failed'),
                func.avg(func.extract('epoch', PipelineRun.end_time - PipelineRun.start_time)).label('avg_duration')
            ).filter(
                PipelineRun.pipeline_id == pipeline_id,
                PipelineRun.start_time >= start_date,
                PipelineRun.start_time <= end_date
            ).first()
            
            total = stats.total or 0
            successful = stats.successful or 0
            failed = stats.failed or 0
            avg_duration = stats.avg_duration or 0
            success_rate = (successful / total * 100) if total > 0 else 0
            
            daily_runs = self.db.query(
                func.date(PipelineRun.start_time).label('date'),
                PipelineRun.status
            ).filter(
                PipelineRun.pipeline_id == pipeline_id,
                PipelineRun.start_time >= start_date,
                PipelineRun.start_time <= end_date
            ).all()
            
            date_groups = {}
            for run in daily_runs:
                date_str = run.date.isoformat() if run.date else None
                if date_str not in date_groups:
                    date_groups[date_str] = {"total_runs": 0, "successful_runs": 0, "failed_runs": 0}
                
                date_groups[date_str]["total_runs"] += 1
                if run.status == "SUCCESS":
                    date_groups[date_str]["successful_runs"] += 1
                elif run.status == "FAILED":
                    date_groups[date_str]["failed_runs"] += 1
            
            daily_runs_data = [
                {
                    "date": date,
                    "total_runs": data["total_runs"],
                    "successful_runs": data["successful_runs"],
                    "failed_runs": data["failed_runs"],
                    "success_rate": round((data["successful_runs"] / data["total_runs"] * 100), 2) if data["total_runs"] > 0 else 0
                }
                for date, data in sorted(date_groups.items())
            ]
            
            all_runs = self.db.query(PipelineRun).filter(
                PipelineRun.pipeline_id == pipeline_id,
                PipelineRun.start_time >= start_date,
                PipelineRun.start_time <= end_date,
                PipelineRun.start_time.isnot(None),
                PipelineRun.end_time.isnot(None)
            ).all()
            
            success_durations = []
            failure_durations = []
            
            for run in all_runs:
                duration = (run.end_time - run.start_time).total_seconds()
                if duration > 0:
                    if run.status == "SUCCESS":
                        success_durations.append(duration)
                    elif run.status == "FAILED":
                        failure_durations.append(duration)
            
            duration_distribution = [
                {
                    "range": bucket["range"],
                    "success_count": bucket["success_count"],
                    "failure_count": bucket["failure_count"],
                    "count": bucket["total_count"]
                }
                for bucket in self._create_duration_bins(success_durations, failure_durations)
            ]
            
            return {
                "pipeline_info": {
                    "pipeline_id": pipeline.pipeline_id,
                    "name": pipeline.name,
                    "description": pipeline.description,
                    "step_count": len(pipeline.steps) if pipeline.steps else 0,
                    "created_at": pipeline.created_at.isoformat() if pipeline.created_at else None,
                    "is_deprecated": pipeline.is_deprecated
                },
                "stats": {
                    "total_runs": total,
                    "successful_runs": successful,
                    "failed_runs": failed,
                    "success_rate": round(success_rate, 2),
                    "avg_duration_formatted": self._format_duration(avg_duration)
                },
                "charts": {
                    "daily_runs": daily_runs_data,
                    "duration_distribution": duration_distribution
                },
                "days_filter": days,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": f"Failed to get pipeline analytics: {str(e)}",
                "pipeline_info": {},
                "stats": {"total_runs": 0, "successful_runs": 0, "failed_runs": 0, "success_rate": 0, "avg_duration_formatted": "0m 0s"},
                "charts": {"daily_runs": [], "duration_distribution": []},
                "days_filter": days,
                "generated_at": datetime.now().isoformat()
            }
