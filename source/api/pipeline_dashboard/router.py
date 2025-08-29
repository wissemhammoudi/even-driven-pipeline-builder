from fastapi import APIRouter, HTTPException, Depends, status
from source.service.pipeline_dashboard.service import PipelineDashboardService
from source.config.config import api_config
from source.service.authentication.keycloak_auth import KeycloakAuthService

pipeline_dashboard_router = APIRouter(prefix=f"{api_config.api_prefix}/pipeline-dashboard")

@pipeline_dashboard_router.get("/pipeline/{pipeline_id}/analytics")
def get_pipeline_analytics(
    pipeline_id: int,
    days: int = 30,
    pipeline_dashboard_service: PipelineDashboardService = Depends(PipelineDashboardService),
    current_user: dict = Depends(KeycloakAuthService.require_user_role)
):

    try:
        return pipeline_dashboard_service.get_pipeline_analytics(pipeline_id, days)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving pipeline analytics: {str(e)}"
        )