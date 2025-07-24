from source.models.dashboard_pipline_association.models import DashboardPipelineAssociation
from source.repository.database import get_db
from typing import List

class DashboardPipelineAssociationRepository:
    def __init__(self):
        self.db = get_db()

    def create_association(self, pipeline_id: int, dashboard_id: int) -> DashboardPipelineAssociation:
        association = DashboardPipelineAssociation(
            pipeline_id=pipeline_id,
            dashboard_id=dashboard_id
        )
        self.db.add(association)
        self.db.commit()
        self.db.refresh(association)
        return association

    def get_by_pipeline_id(self, pipeline_id: int) -> List[DashboardPipelineAssociation]:
        return self.db.query(DashboardPipelineAssociation).filter(
            DashboardPipelineAssociation.pipeline_id == pipeline_id
        ).all() 