from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta
from source.models.pipeline.models import Pipeline
from source.models.pipeline_run.model import PipelineRun
from source.repository.database import get_db

class DashboardRepository:
    def __init__(self):
        self.db: Session = next(get_db())
    
    def _format_duration(self, seconds: float) -> str:
        if seconds <= 0:
            return "0m 0s"
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    
    def get_pipeline_stats_by_ids(self, pipeline_ids: List[int]) -> Dict[str, Any]:
        """Get pipeline statistics for given pipeline IDs"""
        try:
            total = self.db.query(Pipeline).filter(Pipeline.pipeline_id.in_(pipeline_ids)).count()
            active = self.db.query(Pipeline).filter(
                Pipeline.pipeline_id.in_(pipeline_ids),
                Pipeline.is_deprecated == False
            ).count()
            deprecated = self.db.query(Pipeline).filter(
                Pipeline.pipeline_id.in_(pipeline_ids),
                Pipeline.is_deprecated == True
            ).count()
            
            return {
                "total": total,
                "active": active,
                "deprecated": deprecated
            }
        except Exception as e:
            print(f"Error getting pipeline stats: {e}")
            return {"total": 0, "active": 0, "deprecated": 0}
    
    def get_pipeline_run_stats_by_ids(self, pipeline_ids: List[int]) -> Dict[str, Any]:
        """Get pipeline run statistics for given pipeline IDs"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            stats = self.db.query(
                func.count(PipelineRun.run_id).label('total'),
                func.sum(case((PipelineRun.status == "SUCCESS", 1), else_=0)).label('successful'),
                func.sum(case((PipelineRun.status == "FAILED", 1), else_=0)).label('failed'),
                func.avg(func.extract('epoch', PipelineRun.end_time - PipelineRun.start_time)).label('avg_duration')
            ).filter(
                PipelineRun.pipeline_id.in_(pipeline_ids),
                PipelineRun.start_time >= start_date,
                PipelineRun.start_time <= end_date
            ).first()
            
            total = stats.total or 0
            successful = stats.successful or 0
            failed = stats.failed or 0
            avg_duration = stats.avg_duration or 0
            success_rate = (successful / total * 100) if total > 0 else 0
            
            return {
                "total": total,
                "successful": successful,
                "failed": failed,
                "success_rate": round(success_rate, 2),
                "avg_duration_formatted": self._format_duration(avg_duration)
            }
        except Exception as e:
            print(f"Error getting run stats: {e}")
            return {"total": 0, "successful": 0, "failed": 0, "success_rate": 0, "avg_duration_formatted": "0m 0s"}
    
    def get_recent_pipelines_by_ids(self, limit: int = 5, pipeline_ids: List[int] = None) -> List[Dict[str, Any]]:
        """Get recent pipelines for given pipeline IDs"""
        try:
            query = self.db.query(Pipeline)
            if pipeline_ids:
                query = query.filter(Pipeline.pipeline_id.in_(pipeline_ids))
            
            pipelines = query.order_by(Pipeline.created_at.desc()).limit(limit).all()
            
            result = []
            for pipeline in pipelines:
                step_count = len(pipeline.steps) if pipeline.steps else 0
                result.append({
                    "pipeline_id": pipeline.pipeline_id,
                    "name": pipeline.name,
                    "description": pipeline.description,
                    "status": "ACTIVE" if not pipeline.is_deprecated else "DEPRECATED",
                    "created_at": pipeline.created_at.isoformat() if pipeline.created_at else None,
                    "created_by": pipeline.created_by,
                    "step_count": step_count
                })
            
            return result
        except Exception as e:
            print(f"Error getting recent pipelines: {e}")
            return []
    
    def get_pipeline_creation_trend_by_ids(self, days: int = 30, pipeline_ids: List[int] = None) -> List[Dict[str, Any]]:
        """Get pipeline creation trend for given pipeline IDs"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            query = self.db.query(
                func.date(Pipeline.created_at).label('date'),
                func.count(Pipeline.pipeline_id).label('count')
            ).filter(Pipeline.created_at >= start_date, Pipeline.created_at <= end_date)
            
            if pipeline_ids:
                query = query.filter(Pipeline.pipeline_id.in_(pipeline_ids))
            
            results = query.group_by(func.date(Pipeline.created_at)).all()
            
            trend_data = []
            for result in results:
                if result.date:
                    trend_data.append({
                        "date": result.date.isoformat(),
                        "count": result.count
                    })
            
            return trend_data
        except Exception as e:
            print(f"Error getting creation trend: {e}")
            return []
    
    def get_pipeline_status_distribution_by_ids(self, pipeline_ids: List[int] = None) -> List[Dict[str, Any]]:
        """Get pipeline status distribution for given pipeline IDs"""
        try:
            query = self.db.query(
                case((Pipeline.is_deprecated == True, "DEPRECATED"), else_="ACTIVE").label('status'),
                func.count(Pipeline.pipeline_id).label('count')
            )
            
            if pipeline_ids:
                query = query.filter(Pipeline.pipeline_id.in_(pipeline_ids))
            
            results = query.group_by(case((Pipeline.is_deprecated == True, "DEPRECATED"), else_="ACTIVE")).all()
            
            distribution = []
            for result in results:
                distribution.append({
                    "status": result.status,
                    "count": result.count
                })
            
            return distribution
        except Exception as e:
            print(f"Error getting status distribution: {e}")
            return []
    
    def get_success_failure_distribution_by_ids(self, pipeline_ids: List[int] = None) -> List[Dict[str, Any]]:
        """Get success/failure distribution for given pipeline IDs"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            query = self.db.query(
                PipelineRun.status,
                func.count(PipelineRun.run_id).label('count')
            ).filter(
                PipelineRun.start_time >= start_date,
                PipelineRun.start_time <= end_date
            )
            
            if pipeline_ids:
                query = query.filter(PipelineRun.pipeline_id.in_(pipeline_ids))
            
            results = query.group_by(PipelineRun.status).all()
            
            distribution = []
            for result in results:
                if result.status in ["SUCCESS", "FAILED"]:
                    distribution.append({
                        "status": result.status,
                        "count": result.count
                    })
            
            return distribution
        except Exception as e:
            print(f"Error getting success/failure distribution: {e}")
            return []

