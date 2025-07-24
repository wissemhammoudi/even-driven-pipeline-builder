from typing import Dict, Any
from source.repository.pipeline_dashboard.repository import PipelineDashboardRepository
from source.repository.database import get_db

database = get_db()

class PipelineDashboardService:
    def __init__(self):
        self.db = database
        self.pipeline_dashboard_repository = PipelineDashboardRepository()
    
    def get_pipeline_analytics(self, pipeline_id: int, days: int = 30) -> Dict[str, Any]:
        try:
            return self.pipeline_dashboard_repository.get_pipeline_analytics(pipeline_id, days)
        except Exception as e:
            print(f"Error getting pipeline analytics: {e}")
            return {}