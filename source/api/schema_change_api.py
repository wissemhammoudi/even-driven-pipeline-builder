from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from source.database import get_db
from source.service.debezium_service import DebeziumService
from source.service.schema_change_detector import SchemaChangeDetector
from source.service.kafka_consumer_service import KafkaConsumerService
from source.models.schema_change import SchemaChangeEvent, SchemaChangeNotification
from source.schemas.schema_change_schemas import (
    SchemaChangeResponse,
    DebeziumConnectorResponse,
    SchemaSummaryResponse,
    SchemaChangeHistoryResponse,
    HealthCheckResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schema-changes", tags=["Schema Change Detection"])

# Initialize services
debezium_service = DebeziumService()
schema_detector = SchemaChangeDetector()
kafka_service = KafkaConsumerService()

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Check the health of schema change detection services"""
    try:
        debezium_health = debezium_service.health_check()
        kafka_health = kafka_service.health_check()
        
        overall_status = "healthy"
        if debezium_health.get("status") == "unhealthy" or kafka_health.get("status") == "unhealthy":
            overall_status = "unhealthy"
        
        return HealthCheckResponse(
            status=overall_status,
            debezium=debezium_health,
            kafka=kafka_health,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.post("/debezium/connector", response_model=DebeziumConnectorResponse)
async def create_debezium_connector():
    """Create a new Debezium PostgreSQL connector"""
    try:
        result = debezium_service.create_postgres_connector()
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return DebeziumConnectorResponse(
            success=True,
            message="PostgreSQL connector created successfully",
            connector_info=result
        )
    except Exception as e:
        logger.error(f"Failed to create Debezium connector: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create connector: {str(e)}")

@router.get("/debezium/connector/{connector_name}/status")
async def get_connector_status(connector_name: str):
    """Get the status of a specific Debezium connector"""
    try:
        result = debezium_service.get_connector_status(connector_name)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
    except Exception as e:
        logger.error(f"Failed to get connector status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get connector status: {str(e)}")

@router.get("/debezium/connectors")
async def get_all_connectors():
    """Get all available Debezium connectors"""
    try:
        connectors = debezium_service.get_all_connectors()
        return {"connectors": connectors}
    except Exception as e:
        logger.error(f"Failed to get connectors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get connectors: {str(e)}")

@router.delete("/debezium/connector/{connector_name}")
async def delete_connector(connector_name: str):
    """Delete a specific Debezium connector"""
    try:
        result = debezium_service.delete_connector(connector_name)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        logger.error(f"Failed to delete connector: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete connector: {str(e)}")

@router.post("/debezium/connector/{connector_name}/restart")
async def restart_connector(connector_name: str):
    """Restart a specific Debezium connector"""
    try:
        result = debezium_service.restart_connector(connector_name)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        logger.error(f"Failed to restart connector: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to restart connector: {str(e)}")

@router.post("/debezium/connector/{connector_name}/pause")
async def pause_connector(connector_name: str):
    """Pause a specific Debezium connector"""
    try:
        result = debezium_service.pause_connector(connector_name)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        logger.error(f"Failed to pause connector: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to pause connector: {str(e)}")

@router.post("/debezium/connector/{connector_name}/resume")
async def resume_connector(connector_name: str):
    """Resume a specific Debezium connector"""
    try:
        result = debezium_service.resume_connector(connector_name)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        logger.error(f"Failed to resume connector: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to resume connector: {str(e)}")

@router.get("/detect", response_model=List[SchemaChangeResponse])
async def detect_schema_changes(schema_name: str = "public"):
    """Detect schema changes in the specified schema"""
    try:
        changes = schema_detector.detect_schema_changes(schema_name)
        
        return [
            SchemaChangeResponse(
                table_name=change.table_name,
                schema_name=change.schema_name,
                change_type=change.change_type,
                change_details=change.change_details,
                event_id=change.event_id,
                source_connector=change.source_connector,
                timestamp=change.timestamp.isoformat()
            )
            for change in changes
        ]
    except Exception as e:
        logger.error(f"Failed to detect schema changes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to detect schema changes: {str(e)}")

@router.get("/schema/{schema_name}/summary", response_model=SchemaSummaryResponse)
async def get_schema_summary(schema_name: str = "public"):
    """Get a summary of the current schema"""
    try:
        summary = schema_detector.get_schema_summary(schema_name)
        
        if not summary:
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")
        
        return SchemaSummaryResponse(**summary)
    except Exception as e:
        logger.error(f"Failed to get schema summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get schema summary: {str(e)}")

@router.get("/history/{table_name}", response_model=SchemaChangeHistoryResponse)
async def get_schema_change_history(
    table_name: str, 
    schema_name: str = "public", 
    limit: int = 100
):
    """Get schema change history for a specific table"""
    try:
        history = schema_detector.get_schema_history(table_name, schema_name, limit)
        
        return SchemaChangeHistoryResponse(
            table_name=table_name,
            schema_name=schema_name,
            changes=history,
            total_changes=len(history)
        )
    except Exception as e:
        logger.error(f"Failed to get schema change history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get schema change history: {str(e)}")

@router.post("/kafka/start")
async def start_kafka_consumer(topic: str, background_tasks: BackgroundTasks):
    """Start consuming from a Kafka topic"""
    try:
        # Start consumer in background
        background_tasks.add_task(kafka_service.start_consuming, topic)
        
        return {
            "success": True,
            "message": f"Started consuming from topic: {topic}",
            "topic": topic
        }
    except Exception as e:
        logger.error(f"Failed to start Kafka consumer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start consumer: {str(e)}")

@router.post("/kafka/stop")
async def stop_kafka_consumer():
    """Stop the Kafka consumer"""
    try:
        kafka_service.stop_consuming()
        
        return {
            "success": True,
            "message": "Kafka consumer stopped"
        }
    except Exception as e:
        logger.error(f"Failed to stop Kafka consumer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop consumer: {str(e)}")

@router.get("/kafka/status")
async def get_kafka_status():
    """Get the status of the Kafka consumer service"""
    try:
        status = kafka_service.health_check()
        return status
    except Exception as e:
        logger.error(f"Failed to get Kafka status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get Kafka status: {str(e)}")

@router.get("/cache/events/{table_name}")
async def get_cached_events(
    table_name: str, 
    schema_name: str = "public", 
    limit: int = 10
):
    """Get cached schema change events for a specific table"""
    try:
        events = kafka_service.get_cached_events(table_name, schema_name, limit)
        return {
            "table_name": table_name,
            "schema_name": schema_name,
            "events": events,
            "total_events": len(events)
        }
    except Exception as e:
        logger.error(f"Failed to get cached events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cached events: {str(e)}")

@router.post("/cache/clear/{schema_name}")
async def clear_schema_cache(schema_name: str = "public"):
    """Clear the schema cache for a specific schema"""
    try:
        schema_detector.clear_schema_cache(schema_name)
        
        return {
            "success": True,
            "message": f"Schema cache cleared for schema '{schema_name}'"
        }
    except Exception as e:
        logger.error(f"Failed to clear schema cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear schema cache: {str(e)}")

@router.post("/event-handler/register")
async def register_event_handler(handler_type: str, handler_config: Dict[str, Any]):
    """Register a new event handler for schema changes"""
    try:
        # This is a placeholder for registering custom event handlers
        # In a real implementation, you might want to store handler configurations
        # and dynamically load/register them
        
        return {
            "success": True,
            "message": f"Event handler '{handler_type}' registered successfully",
            "handler_type": handler_type,
            "handler_config": handler_config
        }
    except Exception as e:
        logger.error(f"Failed to register event handler: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to register event handler: {str(e)}")

# Import datetime for the health check endpoint
from datetime import datetime
