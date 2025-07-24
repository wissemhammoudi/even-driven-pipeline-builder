from typing import Dict, Any, List, Optional
from datetime import datetime
from source.repository.dashboard.repository import DashboardRepository

class DashboardService:
    def __init__(self):
        self.dashboard_repository = DashboardRepository()

    def get_dashboard_data_by_pipeline_ids(self, pipeline_ids: List[int]) -> Dict[str, Any]:
        try:
            stats = self.get_dashboard_stats_by_pipeline_ids(pipeline_ids)
            charts_data = self.get_charts_data_by_pipeline_ids(30, pipeline_ids)
            recent_pipelines = self.get_recent_pipelines_by_pipeline_ids(5, pipeline_ids)
            
            return {
                "stats": stats,
                "charts": charts_data,
                "recent_pipelines": recent_pipelines,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error in get_dashboard_data_by_pipeline_ids: {e}")
            return {
                "stats": {"pipelines": {"total": 0, "active": 0, "deprecated": 0}, "runs": {"total": 0, "successful": 0, "failed": 0, "success_rate": 0, "avg_duration_formatted": "0m 0s"}},
                "charts": {
                    "pipeline_creation_trend": [],
                    "pipeline_status_distribution": [],
                    "success_failure_distribution": [],
                    "days_filter": 30
                },
                "recent_pipelines": [],
                "generated_at": datetime.now().isoformat()
            }

    def get_dashboard_stats_by_pipeline_ids(self, pipeline_ids: List[int]) -> Dict[str, Any]:
        try:
            pipeline_stats = self.dashboard_repository.get_pipeline_stats_by_ids(pipeline_ids)
            run_stats = self.dashboard_repository.get_pipeline_run_stats_by_ids(pipeline_ids)
            
            return {
                "pipelines": pipeline_stats,
                "runs": run_stats
            }
        except Exception as e:
            print(f"Error in get_dashboard_stats_by_pipeline_ids: {e}")
            return {
                "pipelines": {"total": 0, "active": 0, "deprecated": 0},
                "runs": {"total": 0, "successful": 0, "failed": 0, "success_rate": 0, "avg_duration_formatted": "0m 0s"}
            }

    def get_recent_pipelines_by_pipeline_ids(self, limit: int = 5, pipeline_ids: List[int] = None) -> List[Dict[str, Any]]:
        try:
            return self.dashboard_repository.get_recent_pipelines_by_ids(limit, pipeline_ids)
        except Exception as e:
            print(f"Error in get_recent_pipelines_by_pipeline_ids: {e}")
            return []

    def get_charts_data_by_pipeline_ids(self, days: int = 30, pipeline_ids: List[int] = None) -> Dict[str, Any]:
        try:
            pipeline_creation_trend = self.dashboard_repository.get_pipeline_creation_trend_by_ids(days, pipeline_ids)
            pipeline_status_distribution = self.dashboard_repository.get_pipeline_status_distribution_by_ids(pipeline_ids)
            success_failure_distribution = self.dashboard_repository.get_success_failure_distribution_by_ids(pipeline_ids)
            
            return {
                "pipeline_creation_trend": pipeline_creation_trend,
                "pipeline_status_distribution": pipeline_status_distribution,
                "success_failure_distribution": success_failure_distribution,
                "days_filter": days
            }
        except Exception as e:
            print(f"Error in get_charts_data_by_pipeline_ids: {e}")
            return {
                "pipeline_creation_trend": [],
                "pipeline_status_distribution": [],
                "success_failure_distribution": [],
                "days_filter": days
            }

