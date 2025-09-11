import logging
from typing import Dict, Any
from datetime import datetime, timezone
from source.service.change_detection.kafka_service import KafkaService
from source.service.change_detection.debezium_service import DebeziumService
from source.service.change_detection.redis_service import RedisService
from source.repository.pipeline_run.repository import PipelineRunRepository
from source.models.pipeline_run.model import PipelineRun
from source.service.pipeline.service import PipelineService
from source.service.change_detection.message_orchestrator_service import MessageOrchestratorService
from source.repository.pipeline.repository import PipelineRepository

class CDCService:
    
    def __init__(self):
        self.kafka_service = KafkaService()
        self.debezium_service = DebeziumService()
        self.redis_service = RedisService()
        self.pipeline_run_repo = PipelineRunRepository()
        self.pipeline_service = PipelineService()
        self.message_orchestrator = MessageOrchestratorService()
        self.pipeline_repo = PipelineRepository()
        self.connectors: Dict[str, Dict[str, Any]] = {}
        self.consumers: Dict[str, Any] = {}
        self._is_initialized = False
        
    async def initialize(self) -> bool:
        try:
            kafka_init = await self.kafka_service.initialize()
            debezium_init = await self.debezium_service.initialize()
            redis_init = await self.redis_service.initialize()
            orchestrator_init = await self.message_orchestrator.initialize()
            if all([kafka_init, debezium_init, redis_init, orchestrator_init]):
                self._is_initialized = True
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    async def close(self) -> bool:
        try:
            for consumer_name, consumer in self.consumers.items():
                try:
                    await consumer.close()
                except Exception as e:
                    pass
            
            await self.kafka_service.close()
            await self.debezium_service.close()
            await self.redis_service.close()
            
            self.connectors.clear()
            self.consumers.clear()
            self._is_initialized = False
            return True
            
        except Exception as e:
            return False
    
    async def start_schema_monitoring(self, pipeline_id: int, initiator_user_id: str | None = None) -> Dict[str, Any]:
        try:
            if not self._is_initialized:
                return {"error": "CDC service not initialized"}
            
            pipeline_config = await self.redis_service.get_cache_data("pipeline_config", str(pipeline_id))
            if not pipeline_config:
                try:
                    pipeline_repo = self.pipeline_repo
                    conn_cfg = pipeline_repo.get_ingestion_source_config_by_pipeline_id(pipeline_id) or {}
                    source_cfg = conn_cfg.get("source") or conn_cfg.get("extractor") or {}
                    
                    host = source_cfg.get("host") or source_cfg.get("hostname")
                    port = str(source_cfg.get("port") or "5432")
                    user = source_cfg.get("username") or source_cfg.get("user")
                    password = source_cfg.get("password")
                    dbname = source_cfg.get("database") or source_cfg.get("dbname")

                    missing_fields = [
                        name for name, val in [
                            ("host", host),
                            ("port", port),
                            ("user", user),
                            ("password", password),
                            ("dbname", dbname),
                        ] if not val
                    ]
                    if missing_fields:
                        raise ValueError("Incomplete source configuration in ingestion step")
                    
                    pipeline_config = {
                        "database_config": {
                            "host": host,
                            "port": port,
                            "user": user,
                            "password": password,
                            "dbname": dbname,
                        }
                    }
                    
                except Exception as _e:
                    return {"error": f"Pipeline configuration for id '{pipeline_id}' not found and could not be derived from ingestion step: {_e}"}
            
            connector_config = {
                "database.hostname": pipeline_config.get("database_config", {}).get("host"),
                "database.port": pipeline_config.get("database_config", {}).get("port", "5432"),
                "database.user": pipeline_config.get("database_config", {}).get("user"),
                "database.password": pipeline_config.get("database_config", {}).get("password"),
                "database.dbname": pipeline_config.get("database_config", {}).get("dbname"),
                "topic.prefix": f"pipeline-{pipeline_id}-schema",
                "database.server.name": f"pipeline-{pipeline_id}-schema",
                "database.server.id": "2",
                "schema.history.internal.kafka.bootstrap.servers": self.kafka_service.kafka_broker,
                "schema.history.internal.kafka.topic": f"pipeline-{pipeline_id}-schema.dbhistory",
                "plugin.name": "pgoutput",
                "publication.autocreate.mode": "filtered",
                "schema.include.list": "public",
                "table.include.list": "public.*",
                "slot.drop.on.stop": "true",
                "include.schema.changes": "true"
            }
            
            connector_name = f"pipeline-{pipeline_id}-schema-monitor"
            connector_result = await self.debezium_service.create_connector(
                connector_name, "postgresql", connector_config
            )
            
            if "error" in connector_result:
                error_msg = connector_result['error']
                if "Missing required configuration" in error_msg:
                    return {
                        "error": "Database configuration incomplete",
                        "context": {
                            "message": error_msg,
                            "pipeline_id": pipeline_id,
                            "connector_name": connector_name,
                        }
                    }
                elif "already exists" in error_msg:
                    pass
                else:
                    safe_cfg = {
                        "database.hostname": connector_config.get("database.hostname"),
                        "database.port": connector_config.get("database.port"),
                        "database.user": connector_config.get("database.user"),
                        "database.dbname": connector_config.get("database.dbname"),
                        "topic.prefix": connector_config.get("topic.prefix"),
                        "database.server.name": connector_config.get("database.server.name"),
                    }
                    return {
                        "error": "Failed to create Debezium connector",
                        "context": {
                            "message": error_msg,
                            "pipeline_id": pipeline_id,
                            "connector_name": connector_name,
                            "sanitized_config": safe_cfg,
                        }
                    }
            
            self.connectors[connector_name] = {
                "connector_name": connector_name,
                "pipeline_id": pipeline_id,
                "topic_name": f"pipeline-{pipeline_id}-schema"
            }
            
            topic_name = f"pipeline-{pipeline_id}-schema"
            # Subscribe only to per-table data topics
            topic_pattern = f"^{topic_name}\.public\..*"
            
            consumer_start = await self.message_orchestrator.start_consumer(
                pipeline_name=topic_name,
                topic=topic_pattern
            )
            
            if not consumer_start.get("success"):
                err = consumer_start.get("error", "unknown error")
                if "already running" in err.lower() or "already exists" in err.lower():
                    consumer_name = f"{topic_name}-consumer"
                else:
                    await self.debezium_service.delete_connector(connector_name)
                    del self.connectors[connector_name]
                    return {
                        "error": "Failed to start consumer",
                        "context": {
                            "message": err,
                            "pipeline_id": pipeline_id,
                            "topic_pattern": topic_pattern,
                            "proposed_consumer_id": f"{topic_name}-schema-consumer",
                        }
                    }
            else:
                consumer_name = consumer_start.get("consumer_id", f"{topic_name}-consumer")

            # Using the single consumer for data topics, keep the same consumer name
            data_consumer_name = consumer_name
            
            await self.redis_service.set_cache_data(
                "schema_monitoring", str(pipeline_id), 
                {
                    "enabled": True, 
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "connector_name": connector_name,
                    "consumer_name": consumer_name,
                    "data_consumer_name": data_consumer_name,
                    "topic_name": topic_name,
                    "initiator_user_id": initiator_user_id
                }
            )
            
            try:
                pipeline = self.pipeline_service.get_pipline_by_id(pipeline_id)
                if pipeline:
                    pipeline.status = "RUNNING"
                    self.pipeline_service.pipeline_repository.commit()
                
                created_by = getattr(pipeline, "created_by", None) if pipeline else "system"
                run_entry = PipelineRun(
                    pipeline_id=pipeline_id,
                    created_by=created_by,
                    pipeline_run="RUNNING",
                    start_time=datetime.now(timezone.utc)
                )
                self.pipeline_run_repo.create(run_entry)
            except Exception as _e:
                pass
            
            return {
                "success": True,
                "pipeline_id": pipeline_id,
                "connector_name": connector_name,
                "consumer_name": consumer_name,
                "data_consumer_name": data_consumer_name,
                "topic_name": topic_name,
                "message": "Schema monitoring started successfully"
            }
            
        except Exception as e:
            return {"error": f"Error starting schema monitoring: {str(e)}"}
    
    async def stop_schema_monitoring(self, pipeline_id: int) -> Dict[str, Any]:
        try:
            if not self._is_initialized:
                return {"error": "CDC service not initialized"}
            
            schema_config = await self.redis_service.get_cache_data("schema_monitoring", str(pipeline_id))
            if not schema_config:
                return {"error": f"Schema monitoring not configured for pipeline id '{pipeline_id}'"}
            
            connector_name = schema_config.get("connector_name")
            consumer_name = schema_config.get("consumer_name")
            
            if consumer_name:
                try:
                    await self.message_orchestrator.stop_consumer(consumer_name)
                except Exception as e:
                    pass
            
            if connector_name and connector_name in self.connectors:
                await self.debezium_service.delete_connector(connector_name)
                del self.connectors[connector_name]
            
            await self.redis_service.set_cache_data(
                "schema_monitoring", str(pipeline_id), 
                {
                    "enabled": False, 
                    "stopped_at": datetime.now(timezone.utc).isoformat(),
                    "connector_name": connector_name,
                    "consumer_name": consumer_name
                }
            )
            
            try:
                pipeline = self.pipeline_service.get_pipline_by_id(pipeline_id)
                if pipeline:
                    pipeline.status = "STOPPED"
                    self.pipeline_service.pipeline_repository.commit()
            except Exception as _e:
                pass
            
            return {
                "success": True,
                "pipeline_id": pipeline_id,
                "message": "Schema monitoring stopped successfully"
            }
            
        except Exception as e:
            return {"error": f"Error stopping schema monitoring: {str(e)}"}
       
    async def list_internal_consumers(self) -> Dict[str, Any]:
        try:
            return await self.message_orchestrator.list_consumers()
        except Exception as e:
            return {"error": f"Error listing internal consumers: {str(e)}"}
       
    # Removed schema change handler: this service now only processes data events
    
    @property
    def is_initialized(self) -> bool:
        return self._is_initialized