from source.repository.dashboard_pipline_association.repository import DashboardPipelineAssociationRepository
from source.models.dashboard_pipline_association.models import DashboardPipelineAssociation
from typing import List

class DashboardPipelineAssociationService:
    def __init__(self):
        self.repository = DashboardPipelineAssociationRepository()

    def create_association(self, pipeline_id: int, dashboard_id: int) -> DashboardPipelineAssociation:
        return self.repository.create_association(pipeline_id, dashboard_id)

    def get_by_pipeline_id(self, pipeline_id: int) -> List[DashboardPipelineAssociation]:
        return self.repository.get_by_pipeline_id(pipeline_id) 