from fastapi import APIRouter, Depends, HTTPException, status
from source.service.dashboard.service import DashboardService
from source.service.user_pipeline_access.service import UserPipelineAccessService
from source.config.config import settings

dashboard_router = APIRouter(prefix=f"{settings.base_url}/dashboard", tags=["Dashboard"])

@dashboard_router.get("/")
def get_dashboard_data(
    user_id: int,
    dashboard_service: DashboardService = Depends(DashboardService),
    user_pipeline_access_service: UserPipelineAccessService = Depends(UserPipelineAccessService)
):
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id is required"
            )
        
        pipeline_ids = user_pipeline_access_service._get_user_pipeline_ids(user_id)
        return dashboard_service.get_dashboard_data_by_pipeline_ids(pipeline_ids)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving dashboard data: {str(e)}"
        )

@dashboard_router.get("/charts")
def get_charts_data(
    user_id: int,
    days: int = 7,
    dashboard_service: DashboardService = Depends(DashboardService),
    user_pipeline_access_service: UserPipelineAccessService = Depends(UserPipelineAccessService)
):      
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id is required"
            )
        
        pipeline_ids = user_pipeline_access_service._get_user_pipeline_ids(user_id)
        return dashboard_service.get_charts_data_by_pipeline_ids(days, pipeline_ids)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving charts data: {str(e)}"
        )


