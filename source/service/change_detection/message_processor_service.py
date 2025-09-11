import logging
from typing import Dict, Any, Optional
import os
from datetime import datetime, timezone
from source.service.change_detection.redis_service import RedisService
from source.repository.database import Database
from sqlalchemy.orm import Session
from source.service.pipeline_run.service import PipelineRunService
from source.schema.pipeline_run.schema import PipelineRunCreate

logger = logging.getLogger(__name__)

class MessageProcessorService:
    
    def __init__(self):
        self.redis_service = RedisService()
        self._is_initialized = False
        self._db = Database()
        self._pipeline_run_service = PipelineRunService()
        try:
            self._data_threshold = int(os.getenv("DATA_EVENT_THRESHOLD", "2"))
        except Exception:
            self._data_threshold = 10
        
    async def initialize(self) -> bool:
        try:
            redis_init = await self.redis_service.initialize()
            if redis_init:
                self._is_initialized = True
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self._is_initialized:
                return {"error": "Message Processor service not initialized"}
            
            message_type = self._detect_message_type(message_data)
            
            if message_type == 'data_event':
                result = self._process_data_event(message_data)
                return result
            elif message_type == 'control':
                result = self._process_control(message_data)
                return result
            else:
                result = self._process_unknown(message_data)
                return result
                
        except Exception as e:
            return {"error": f"Error processing message: {str(e)}"}
    
    def _detect_message_type(self, message_data: Dict[str, Any]) -> str:
        try:
            value = message_data.get('value', {})
            topic = message_data.get('topic', '')
            
            if '.public.' in topic:
                return 'data_event'

            if isinstance(value, dict) and 'payload' in value:
                payload = value.get('payload', {})
                operation = payload.get('op')
                if operation in ['c', 'u', 'd']:
                    return 'data_event'
                if operation in ['r', 't']:
                    return 'control'
            
            return 'unknown'
            
        except Exception as e:
            return 'unknown'
    
    
    def _process_data_event(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            value = message_data.get('value') or {}
            if not isinstance(value, dict):
                return {"status": "ignored", "reason": "non-json or tombstone"}

            payload = value.get('payload') or {}
            if not isinstance(payload, dict):
                return {"status": "ignored", "reason": "missing payload"}

            source = payload.get('source') or {}
            if not isinstance(source, dict):
                source = {}
            
            database = source.get('db') or source.get('databaseName')
            schema = source.get('schema') or source.get('schemaName')
            table = source.get('table') or source.get('tableName')
            operation = payload.get('op')
            timestamp = payload.get('ts_ms')

            before_row = payload.get('before') if isinstance(payload.get('before'), dict) else None
            after_row = payload.get('after') if isinstance(payload.get('after'), dict) else None
            
            pipeline_name = self._extract_pipeline_name_from_topic(message_data.get('topic', ''))
            if pipeline_name:
                self._update_event_tracking(pipeline_name, operation, table, schema, database)
                # Threshold counting and trigger
                try:
                    pipeline_id = None
                    try:
                        if 'pipeline-' in pipeline_name and '-schema' in pipeline_name:
                            pipeline_id = int(pipeline_name.split('pipeline-')[1].split('-schema')[0])
                    except Exception:
                        pipeline_id = None
                    if pipeline_id is not None and operation in ['c', 'u', 'd']:
                        self._increment_counters_and_maybe_trigger(pipeline_id, operation, table)
                except Exception:
                    pass
            
            # Store concise CDC record for inspection
            try:
                # Use the initiator_user_id saved when monitoring was started; fallback to None
                initiator = None
                try:
                    if 'pipeline_id' in locals() and pipeline_id is not None and getattr(self.redis_service, 'redis_client', None):
                        key = f"cache:schema_monitoring:{pipeline_id}"
                        raw = self.redis_service.redis_client.get(key)
                        if raw:
                            try:
                                import json
                                schema_mon = json.loads(raw)
                            except Exception:
                                schema_mon = None
                            if isinstance(schema_mon, dict):
                                initiator = schema_mon.get("initiator_user_id")
                except Exception:
                    initiator = None
                event_summary = {
                    "database": database,
                    "schema": schema,
                    "table": table,
                    "operation": operation,
                    "before": before_row,
                    "after": after_row,
                    "ts_ms": timestamp,
                    "topic": message_data.get('topic'),
                    "initiator_user_id": initiator
                }
                import asyncio
                key = f"cdc:{(pipeline_name or 'unknown')}:{(table or 'unknown')}:{datetime.now(timezone.utc).timestamp()}"
                asyncio.create_task(self.redis_service.set_cache_data(
                    "cdc_events", key, event_summary, expiry_seconds=3600
                ))
            except Exception:
                pass

            return {
                "status": "processed",
                "action": "event_tracked",
                "database": database,
                "schema": schema,
                "table": table,
                "operation": operation,
                "has_before": bool(before_row),
                "has_after": bool(after_row)
            }
            
        except Exception as e:
            return {"error": f"Error processing data event: {str(e)}"}

    def _increment_counters_and_maybe_trigger(self, pipeline_id: int, operation: str, table: str) -> None:
        try:
            counters_key = f"event_counters:{pipeline_id}"
            import asyncio
            async def _work():
                data = await self.redis_service.get_cache_data("events", counters_key)
                counters = data or {"c": 0, "u": 0, "d": 0, "tables": {}}
                counters[operation] = counters.get(operation, 0) + 1
                tables = counters.get("tables", {})
                tables[table] = tables.get(table, 0) + 1
                counters["tables"] = tables
                counters["last_ts"] = datetime.now(timezone.utc).isoformat()
                await self.redis_service.set_cache_data("events", counters_key, counters, expiry_seconds=3600)
                total = int(counters.get("c", 0)) + int(counters.get("u", 0)) + int(counters.get("d", 0))
                if total >= self._data_threshold:
                    lock_key = f"pipeline_trigger_lock:{pipeline_id}"
                    lock = await self.redis_service.get_cache_data("locks", lock_key)
                    if not lock:
                        await self.redis_service.set_cache_data("locks", lock_key, {"locked": True}, expiry_seconds=300)
                        try:
                            initiator = None
                            try:
                                if getattr(self.redis_service, 'redis_client', None):
                                    key = f"cache:schema_monitoring:{pipeline_id}"
                                    raw = self.redis_service.redis_client.get(key)
                                    if raw:
                                        try:
                                            import json
                                            schema_mon = json.loads(raw)
                                        except Exception:
                                            schema_mon = None
                                        if isinstance(schema_mon, dict):
                                            initiator = schema_mon.get("initiator_user_id")
                            except Exception:
                                initiator = None
                            run = PipelineRunCreate(pipeline_id=pipeline_id, user_id=initiator)
                            self._pipeline_run_service.start_pipeline(run)
                        except Exception:
                            pass
            asyncio.create_task(_work())
        except Exception:
            pass
    
    def _process_control(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            value = message_data.get('value', {})
            payload = value.get('payload', {})
            operation = payload.get('op')
            timestamp = payload.get('ts_ms')
            
            return {
                "status": "processed",
                "action": "control_handled",
                "operation": operation
            }
            
        except Exception as e:
            return {"error": f"Error processing control message: {str(e)}"}
    
    def _process_unknown(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return {
                "status": "processed",
                "action": "logged_unknown"
            }
            
        except Exception as e:
            return {"error": f"Error processing unknown message: {str(e)}"}
    
    def _store_schema_change(self, database: str, schema: str, table: str, 
                           operation: str, timestamp: int, message_data: Dict[str, Any]) -> None:
        try:
            schema_change_key = f"schema_change_{database}_{schema}_{table}_{timestamp}"
            schema_change_data = {
                "database": database,
                "schema": schema,
                "table": table,
                "operation": operation,
                "timestamp": timestamp,
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "message_data": message_data
            }
            
            import asyncio
            asyncio.create_task(self.redis_service.set_cache_data(
                "schema_changes", schema_change_key, schema_change_data, expiry_seconds=86400
            ))
            
        except Exception as e:
            pass
    
    def _mark_pipeline_broken(self, pipeline_name: str, reason: str, details: Dict[str, Any]) -> None:
        try:
            broken_pipeline_data = {
                "status": "broken",
                "reason": reason,
                "broken_at": datetime.now(timezone.utc).isoformat(),
                "details": details
            }
            
            import asyncio
            asyncio.create_task(self.redis_service.set_cache_data(
                "pipeline_status", pipeline_name, broken_pipeline_data, expiry_seconds=86400
            ))
            
        except Exception as e:
            pass
    
    def _update_event_tracking(self, pipeline_name: str, operation: str, 
                             table: str, schema: str, database: str) -> None:
        try:
            event_key = f"event_{pipeline_name}_{table}_{datetime.now(timezone.utc).timestamp()}"
            event_data = {
                "pipeline_name": pipeline_name,
                "operation": operation,
                "table": table,
                "schema": schema,
                "database": database,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            import asyncio
            asyncio.create_task(self.redis_service.set_cache_data(
                "events", event_key, event_data, expiry_seconds=3600
            ))
            
        except Exception as e:
            pass
    
    def _send_schema_change_notification(self, database: str, schema: str, 
                                       table: str, operation: str, pipeline_name: str) -> None:
        try:
            subject = f"🚨 Schema Change Alert - {database}.{schema}.{table}"
            body = f"""
            A schema change has been detected in your data pipeline.
            
            Details:
            - Database: {database}
            - Schema: {schema}
            - Table: {table}
            - Operation: {operation}
            - Pipeline: {pipeline_name or 'Unknown'}
            - Time: {datetime.now(timezone.utc).isoformat()}
            
            The pipeline has been marked as BROKEN and requires immediate attention.
            
            Please review the schema change and update your pipeline configuration accordingly.
            """
            
            import asyncio
            asyncio.create_task(self.email_service.send_email(
                to=["admin@yourdomain.com"],
                subject=subject,
                body=body
            ))
                
        except Exception as e:
            pass
    
    def _extract_pipeline_name_from_topic(self, topic: str) -> Optional[str]:
        try:
            if not topic:
                return None
            
            # Trim per-table suffix (e.g., pipeline-1-schema.public.table -> pipeline-1-schema)
            if '.public.' in topic:
                topic = topic.split('.public.')[0]
            topic = topic.replace('-schema-changes', '')
            topic = topic.replace('-events', '')
            topic = topic.replace('-changes', '')
            return topic
            
        except Exception as e:
            return None
    
    async def close(self) -> bool:
        try:
            await self.kafka_service.close()
            await self.redis_service.close()
            await self.email_service.close()
            
            self._is_initialized = False
            return True
            
        except Exception as e:
            return False
    
    @property
    def is_initialized(self) -> bool:
        return self._is_initialized