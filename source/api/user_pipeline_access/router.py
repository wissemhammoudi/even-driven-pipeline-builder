from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from source.schema.user_pipeline_acess.schema import (
    UserPipelineAccessUpdate, 
    UserPipelineAccessResponse,
    BulkAccessGrant,
    BulkAccessRevoke,
    BulkOperationResult,
)
from source.service.user_pipeline_access.service import UserPipelineAccessService
from source.exceptions.exceptions import UserNotFoundError, PipelineNotFoundError
from source.config.config import settings

user_pipeline_access_router = APIRouter(
    prefix=f"{settings.api_prefix}/user-pipeline-access"
)
@user_pipeline_access_router.put("/update", response_model=UserPipelineAccessResponse)
def update_access(
    access_data: UserPipelineAccessUpdate,
    user_id: int,
    access_service: UserPipelineAccessService = Depends(UserPipelineAccessService)
):
    try:
        if not access_service.can_manage_access(user_id, access_data.pipeline_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only pipeline owners and administrators can manage access"
            )
        
        access_data.granted_by = user_id
        
        return access_service.update_access(access_data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PipelineNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@user_pipeline_access_router.post("/bulk-grant", response_model=List[UserPipelineAccessResponse])
def bulk_grant_access(
    bulk_data: BulkAccessGrant,
    user_id: int,
    access_service: UserPipelineAccessService = Depends(UserPipelineAccessService)
):
    try:
        if not access_service.can_manage_access(user_id, bulk_data.pipeline_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only pipeline owners and administrators can manage access"
            )
        
        bulk_data.granted_by = user_id
        
        return access_service.bulk_grant_access(
            bulk_data.pipeline_id,
            bulk_data.user_ids,
            bulk_data.grant_type,
            bulk_data.granted_by
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@user_pipeline_access_router.post("/bulk-revoke", response_model=BulkOperationResult)
def bulk_revoke_access(
    bulk_data: BulkAccessRevoke,
    user_id: int,
    access_service: UserPipelineAccessService = Depends(UserPipelineAccessService)
):
    try:
        if not access_service.can_manage_access(user_id, bulk_data.pipeline_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only pipeline owners and administrators can manage access"
            )
        
        return access_service.bulk_revoke_access(bulk_data.pipeline_id, bulk_data.user_ids)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@user_pipeline_access_router.get("/pipeline/{pipeline_id}/users")
def get_users_for_pipeline(
    pipeline_id: int,
    user_id: int,
    access_service: UserPipelineAccessService = Depends(UserPipelineAccessService)
):
    try:
        if not access_service.can_manage_access(user_id, pipeline_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only pipeline owners can view access information"
            )
        
        users = access_service.get_users_for_pipeline(pipeline_id)
        return [
            {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role.value if user.role else None
            }
            for user in users
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@user_pipeline_access_router.get("/pipeline/{pipeline_id}/permissions/{user_id}")
def get_user_permissions(
    pipeline_id: int,
    user_id: int,
    access_service: UserPipelineAccessService = Depends(UserPipelineAccessService)
):
    try:
        permissions = {
            "can_view_pipeline": access_service.can_view_pipeline(user_id, pipeline_id),
            "can_start_pipeline": access_service.can_start_pipeline(user_id, pipeline_id),
            "can_start_visualization": access_service.can_start_visualization(user_id, pipeline_id),
            "can_manage_access": access_service.can_manage_access(user_id, pipeline_id),
            "can_edit_pipeline": access_service.can_edit_pipeline(user_id, pipeline_id),
            "can_delete_pipeline": access_service.can_delete_pipeline(user_id, pipeline_id),
            "user_id": user_id,
            "pipeline_id": pipeline_id
        }
        return permissions
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 