from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy import func, desc, case
from source.models.pipeline.models import Pipeline
from source.models.pipeline_run.model import PipelineRun
from source.models.user.models import User
from source.repository.user_pipeline_access.repository import UserPipelineAccessRepository
from source.repository.database import get_db

database = get_db()

class DashboardRepository:
    def __init__(self):
        self.db = database
        self.user_pipeline_access_repository = UserPipelineAccessRepository()

    def get_pipeline_stats_by_ids(self, pipeline_ids: List[int]) -> Dict[str, int]:
        if not pipeline_ids:
            return {"total": 0, "active": 0, "deprecated": 0}
        
        try:
            stats = self.db.query(
                func.count(Pipeline.pipeline_id).label('total'),
                func.sum(case((Pipeline.is_deprecated == False, 1), else_=0)).label('active')
            ).filter(Pipeline.pipeline_id.in_(pipeline_ids)).first()
            
            total = stats.total or 0
            active = stats.active or 0
            
            return {
                "total": total,
                "active": active,
                "deprecated": total - active
            }
        except Exception:
            return {"total": 0, "active": 0, "deprecated": 0}

    def get_pipeline_run_stats_by_ids(self, pipeline_ids: List[int]) -> Dict[str, Any]:
        if not pipeline_ids:
            return {"total": 0, "successful": 0, "failed": 0, "success_rate": 0, "avg_duration_formatted": "0m 0s"}
        
        try:
            stats = self.db.query(
                func.count(PipelineRun.run_id).label('total'),
                func.sum(case((PipelineRun.status == "SUCCESS", 1), else_=0)).label('successful'),
                func.sum(case((PipelineRun.status == "FAILED", 1), else_=0)).label('failed'),
                func.avg(func.extract('epoch', PipelineRun.end_time - PipelineRun.start_time)).label('avg_duration')
            ).filter(PipelineRun.pipeline_id.in_(pipeline_ids)).first()
            
            total = stats.total or 0
            successful = stats.successful or 0
            failed = stats.failed or 0
            avg_duration = stats.avg_duration or 0
            
            return {
                "total": total,
                "successful": successful,
                "failed": failed,
                "success_rate": round((successful / total * 100), 2) if total > 0 else 0,
                "avg_duration_formatted": f"{int(avg_duration // 60)}m {int(avg_duration % 60)}s" if avg_duration > 0 else "0m 0s"
            }
        except Exception:
            return {"total": 0, "successful": 0, "failed": 0, "success_rate": 0, "avg_duration_formatted": "0m 0s"}

    def get_recent_pipelines_by_ids(self, limit: int = 5, pipeline_ids: List[int] = None) -> List[Dict[str, Any]]:
        if not pipeline_ids:
            return []
        
        try:
            pipelines = self.db.query(Pipeline).join(User, Pipeline.created_by == User.user_id).filter(
                Pipeline.pipeline_id.in_(pipeline_ids)
            ).order_by(desc(Pipeline.created_at)).limit(limit).all()
            
            return [
                {
                    "pipeline_id": p.pipeline_id,
                    "name": p.name,
                    "description": p.description,
                    "status": p.status,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                    "created_by": p.created_by,
                    "username": p.owner.username if p.owner else None,
                    "step_count": len(p.steps) if p.steps else 0
                }
                for p in pipelines
            ]
        except Exception:
            return []

    def get_pipeline_creation_trend_by_ids(self, days: int = 7, pipeline_ids: List[int] = None) -> List[Dict[str, Any]]:
        if not pipeline_ids:
            return []
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            trend = self.db.query(
                func.date(Pipeline.created_at).label('date'),
                func.count(Pipeline.pipeline_id).label('pipelines_created')
            ).filter(
                Pipeline.created_at >= start_date,
                Pipeline.created_at <= end_date,
                Pipeline.pipeline_id.in_(pipeline_ids)
            ).group_by(func.date(Pipeline.created_at)).order_by(func.date(Pipeline.created_at)).all()
            
            return [
                {
                    "date": stat.date.isoformat() if stat.date else None,
                    "pipelines_created": stat.pipelines_created
                }
                for stat in trend
            ]
        except Exception:
            return []

    def get_pipeline_status_distribution_by_ids(self, pipeline_ids: List[int] = None) -> List[Dict[str, Any]]:
        if not pipeline_ids:
            return [{"status": "Active", "count": 0}, {"status": "Deprecated", "count": 0}]
        
        try:
            status_counts = self.db.query(
                Pipeline.is_deprecated,
                func.count(Pipeline.pipeline_id).label('count')
            ).filter(Pipeline.pipeline_id.in_(pipeline_ids)).group_by(Pipeline.is_deprecated).all()
            
            result = [{"status": "Active" if not status else "Deprecated", "count": count} for status, count in status_counts]
            return result if result else [{"status": "Active", "count": 0}, {"status": "Deprecated", "count": 0}]
        except Exception:
            return [{"status": "Active", "count": 0}, {"status": "Deprecated", "count": 0}]

    def get_success_failure_distribution_by_ids(self, pipeline_ids: List[int] = None) -> List[Dict[str, Any]]:
        if not pipeline_ids:
            return [{"status": "SUCCESS", "count": 0, "color": "#05BAEE"}, {"status": "FAILED", "count": 0, "color": "#D6007F"}]
        
        try:
            stats = self.db.query(
                func.sum(case((PipelineRun.status == "SUCCESS", 1), else_=0)).label('successful'),
                func.sum(case((PipelineRun.status == "FAILED", 1), else_=0)).label('failed')
            ).filter(PipelineRun.pipeline_id.in_(pipeline_ids)).first()
            
            return [
                {"status": "SUCCESS", "count": stats.successful or 0, "color": "#05BAEE"},
                {"status": "FAILED", "count": stats.failed or 0, "color": "#D6007F"}
            ]
        except Exception:
            return [{"status": "SUCCESS", "count": 0, "color": "#05BAEE"}, {"status": "FAILED", "count": 0, "color": "#D6007F"}]

