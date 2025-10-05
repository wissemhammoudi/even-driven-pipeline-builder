import threading
import logging
import time
from typing import Dict
from collections import deque
from source.service.change_detection.database_schema_detection.postgres_schema_change import PostgresPipelineSchemaChangeListener, PostgresPipelineDataTracker
from source.repository.pipeline.repository import PipelineRepository
from source.repository.pipeline_step.repository import StepRepository
from source.repository.change_detection.repository import SchemaChangeRepository
from source.service.change_detection.pipeline_config_extractor import PipelineConfigExtractor
from source.service.change_detection.event_processor import EventProcessor
from source.service.pipeline_run.service import PipelineRunService
from source.schema.pipeline_run.schema import PipelineRunCreate
from source.config.config import trigger_conditions_config
import json

class SchemaListenerManager:
    def __init__(self):
        self.pipeline_repo = PipelineRepository()
        self.step_repo = StepRepository()
        self.schema_repository = SchemaChangeRepository()
        self.schema_event_queue = deque() 
        self.data_event_queue = deque() 
        self.event_queue_lock = threading.Lock() 
        self.listeners = {}
        self.data_trackers = {}
        self.processor_thread = None
        self._stop_event = threading.Event()        
        self.config_extractor = PipelineConfigExtractor()
        self.event_processor = EventProcessor(
            self.pipeline_repo,
            self.schema_repository,
            self
        )

    def get_change_tool(self, tool_type: str):
        tool_type = tool_type.lower()
        if tool_type in ['postgresql', 'postgres']:
            return (PostgresPipelineSchemaChangeListener, PostgresPipelineDataTracker)
        else:
            raise ValueError(f"Unsupported change tool: {tool_type}. Supported tools: postgresql, postgres")

    def gather_pipeline_configs(self, pipeline_id: int = None):
        if pipeline_id is not None:
            pipeline_ids = [pipeline_id]
        else:
            pipeline_ids = self.pipeline_repo.get_all_pipelines_ids()
            
        configs = []
        for pid in pipeline_ids:
            pipeline = self.pipeline_repo.get_Active_Pipeline_by_id(pid)
            if not pipeline or pipeline.is_deleted:
                continue
                
            steps = self.step_repo.get_step_by_pipeline(pid)
            if not steps:
                continue
                
            selected_step = self.config_extractor.select_primary_step(steps)
            if not selected_step:
                continue
                
            db_config, schema = self.config_extractor.extract_db_config_and_schema_from_steps(selected_step)
            if not db_config or not schema:
                continue
                
            tables_to_monitor = self.config_extractor.extract_tables_to_monitor_from_steps(selected_step)
            schema_change_tool = self.config_extractor.extract_schema_change_tool_from_steps(selected_step)
            
            threshold_config = {
                'threshold_value': trigger_conditions_config.default_threshold_value,
                'cooldown_period': trigger_conditions_config.cooldown_period
            }
            
            configs.append({
                'db_config': db_config,
                'schema': schema,
                'pipeline_id': pid,
                'tables_to_monitor': tables_to_monitor,
                'schema_change_tool': schema_change_tool,
                'threshold_config': threshold_config
            })
            
        return configs

    def start_all(self):
        configs = self.gather_pipeline_configs()
        
        if len(configs) == 0:
            return
        
        schema_configs = []
        data_configs = []
        for config in configs:
            data_configs.append(config)
            schema_configs.append(config)
        
        configs_by_tool = {}
        for config in schema_configs:
            tool = config.get('schema_change_tool', 'postgresql')
            if tool not in configs_by_tool:
                configs_by_tool[tool] = []
            configs_by_tool[tool].append(config)
        
        for tool, tool_configs in configs_by_tool.items():
            try:
                listener_class, tracker_class = self.get_change_tool(tool)
                listener = listener_class(tool_configs, self.schema_event_queue, self.event_queue_lock)
                listener.start()
                for config in tool_configs:
                    self.listeners[config['pipeline_id']] = listener
            except Exception as e:
                pass
        
        data_configs_by_tool = {}
        for config in data_configs:
            tool = config.get('schema_change_tool', 'postgresql')
            if tool not in data_configs_by_tool:
                data_configs_by_tool[tool] = []
            data_configs_by_tool[tool].append(config)
        
        for tool, tool_configs in data_configs_by_tool.items():
            try:
                listener_class, tracker_class = self.get_change_tool(tool)
                tracker = tracker_class(tool_configs, self.data_event_queue, self.event_queue_lock)
                tracker.start()
                for config in tool_configs:
                    self.data_trackers[config['pipeline_id']] = tracker
            except Exception as e:
                print(f"Error starting data tracker for pipeline {tool_configs[0]['pipeline_id']}: {e}")
        self._stop_event.clear()
        self.processor_thread = threading.Thread(target=self.process_queue, daemon=True)
        self.processor_thread.start()

    def stop_all(self):
        for pipeline_id, listener in self.listeners.items():
            try:
                listener.stop()
            except Exception as e:
                print(f"Error stopping listener for pipeline {pipeline_id}: {e}")
        self.listeners.clear()
        
        for pipeline_id, tracker in self.data_trackers.items():
            try:
                tracker.stop()
            except Exception as e:
                print(f"Error stopping data tracker for pipeline {pipeline_id}: {e}")
        self.data_trackers.clear()
        
        self._stop_event.set()
        if self.processor_thread:
            self.processor_thread.join(timeout=5)

    def start_listener(self, pipeline_id: int):
        if pipeline_id in self.listeners:
            return
        configs = self.gather_pipeline_configs(pipeline_id)
        if not configs:
            return
        
        pipeline_config = configs[0]
        tool = pipeline_config.get('schema_change_tool')
        
        try:
            listener_class, tracker_class = self.get_change_tool(tool)
            listener = listener_class([pipeline_config], self.schema_event_queue, self.event_queue_lock)
            listener.start()
            self.listeners[pipeline_id] = listener            
            
            if not self.processor_thread or not self.processor_thread.is_alive():
                self._stop_event.clear()
                self.processor_thread = threading.Thread(target=self.process_queue, daemon=True)
                self.processor_thread.start()
            
        except Exception as e:
            print(f"Error starting listener for pipeline {pipeline_id}: {e}")

    def stop_listener_on_pipeline_delete(self, pipeline_id: int):
        try:
            if pipeline_id in self.listeners:
                listener = self.listeners[pipeline_id]
                listener.stop()
                del self.listeners[pipeline_id]
        except Exception as e:
            print(f"Error stopping listener for deleted pipeline {pipeline_id}: {e}")

    def process_queue(self):
        while not self._stop_event.is_set():
            try:
                with self.event_queue_lock:
                    if self.schema_event_queue:
                        event = self.schema_event_queue.popleft()
                        self._process_schema_event(event)
                    
                    if self.data_event_queue:
                        event = self.data_event_queue.popleft()
                        self._process_data_event(event)
                    
                    if not self.schema_event_queue and not self.data_event_queue:
                        time.sleep(0.1)
                        
            except Exception as e:
                print(f"Error processing queue: {e}")
                time.sleep(1)

    def _process_schema_event(self, event: dict):
        pipeline_id = int(event['pipeline_id'])
        try:
            result = self.event_processor.process_event(event)
        except Exception as e:
            print(f"Error processing schema event: {e}")

    def _process_data_event(self, event: dict): 
        pipeline_id = int(event['pipeline_id'])
        
        try:
            if event.get('threshold_met'):
                payload_data = json.loads(event.get('payload'))
                timestamp = payload_data.get('timestamp')
                success = self.execute_pipeline(pipeline_id, timestamp)
        except Exception as e:
            print(f"Error processing data event: {e}")

    def execute_pipeline(self, pipeline_id: int, timestamp: str = None):
        try:
            if not isinstance(pipeline_id, int) or pipeline_id <= 0:
                return False
            
            pipeline = self.pipeline_repo.get_pipline_by_id(pipeline_id)
            if not pipeline:
                return False

            user_id = pipeline.created_by if hasattr(pipeline, 'created_by') else 1
            
            pipeline_run_service = PipelineRunService()
            pipeline_run_request = PipelineRunCreate(pipeline_id=pipeline_id, user_id=user_id)
            
            result, status_code = pipeline_run_service.start_pipeline(pipeline_run_request, timestamp)
            
            if status_code != 200:
                return False
            else:
                return True
                
        except Exception as e:
            return False

    def mark_changes_as_synced(self, pipeline_id: int, table_name: str = None):
        try:
            if pipeline_id in self.data_trackers:
                tracker = self.data_trackers[pipeline_id]
                return tracker.mark_changes_as_synced(pipeline_id, table_name)
            else:
                return False
        except Exception as e:
            return False