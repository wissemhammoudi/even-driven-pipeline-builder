from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from source.service.event_driven.cdc_service import CDCService
from source.service.authentication.keycloak_auth import require_user_role
from functools import lru_cache
from source.config.config import api_config

cdc_router = APIRouter(prefix=f"{api_config.api_prefix}/cdc", tags=["Change Data Capture"])

@lru_cache()
def get_cdc_service() -> CDCService:
    return CDCService()

async def get_cdc_service_dependency() -> CDCService:
    """Get CDC service dependency"""
    service = get_cdc_service()
    if not service._is_initialized:
        await service.initialize()
    else:
        print("[CDC DEPENDENCY] CDC service already initialized")
    return service

@cdc_router.post("/pipeline/{pipeline_id}/schema-monitoring/start", response_model=Dict[str, Any])
async def start_schema_monitoring(
    pipeline_id: int,
    cdc_service: CDCService = Depends(get_cdc_service_dependency),
    current_user: dict = Depends(require_user_role)
):
    try:
        initiator_user_id = (
            current_user.get("user_id")
            or current_user.get("id")
            or current_user.get("sub")
            or None
        )
        result = await cdc_service.start_schema_monitoring(pipeline_id, initiator_user_id=initiator_user_id)
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting schema monitoring: {str(e)}"
        )

@cdc_router.post("/pipeline/{pipeline_id}/schema-monitoring/stop", response_model=Dict[str, Any])
async def stop_schema_monitoring(
    pipeline_id: int,
    cdc_service: CDCService = Depends(get_cdc_service_dependency),
    current_user: dict = Depends(require_user_role)
):
    """Stop schema change monitoring for a pipeline"""
    try:
        result = await cdc_service.stop_schema_monitoring(pipeline_id)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error stopping schema monitoring: {str(e)}"
        )


@cdc_router.get("/consumers", response_model=Dict[str, Any])
async def list_consumers(
    cdc_service: CDCService = Depends(get_cdc_service_dependency),
    current_user: dict = Depends(require_user_role)
):
    try:
        result = await cdc_service.list_internal_consumers()
        if "error" in result:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
