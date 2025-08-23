from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from source.schema.pipeline_dashboard.schema import PipelineDashboardCreate, PipelineDashboardUpdate, PipelineDashboardResponse
from source.service.pipeline_dashboard.service import PipelineDashboardService
from source.exceptions.exceptions import PipelineDashboardNotFoundError
from source.config.config import api_config
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from source.service.user.services import UserService
from source.schema.user.schemas import UserRole     
from source.service.authentication.keycloak_auth import get_current_user, require_user_role, require_admin_role 

pipeline_dashboard_router = APIRouter(prefix=f"{api_config.api_prefix}/pipeline-dashboard")

@pipeline_dashboard_router.get("/pipeline/{pipeline_id}/analytics")
def get_pipeline_analytics(
    pipeline_id: int,
    days: int = 30,
    pipeline_dashboard_service: PipelineDashboardService = Depends(PipelineDashboardService),
    current_user: dict = Depends(require_user_role)
):

    try:
        return pipeline_dashboard_service.get_pipeline_analytics(pipeline_id, days)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving pipeline analytics: {str(e)}"
        )