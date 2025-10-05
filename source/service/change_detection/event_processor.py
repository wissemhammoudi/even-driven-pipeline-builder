
import json
import logging
from typing import Dict, Any
from source.service.change_detection.sql_to_humainLanguage.message_generator import SchemaChangeMessageGenerator
from source.schema.change_detection.schema import SchemaChangeTypeEnum
from source.service.email_notification.pipeline_email_notifier import PipelineEmailNotifier

class EventProcessor:
    
    def __init__(self, pipeline_repo, schema_repository, schema_listener_manager=None):
        self.pipeline_repo = pipeline_repo
        self.schema_repository = schema_repository
        self.schema_listener_manager = schema_listener_manager
    
    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        try:
            pipeline_id = int(event['pipeline_id'])
            payload_str = event['payload']
            change_type = event.get('change_type', 'schema')
            
            if change_type != 'schema':
                return {'error': f'Unsupported change type: {change_type}'}
            
            try:
                change_data = json.loads(payload_str)
            except json.JSONDecodeError:
                return {'error': 'Invalid JSON payload'}
            
            pipeline_name = self._get_pipeline_name(pipeline_id)
            
            return self._process_schema_change(event, change_data, pipeline_id, pipeline_name)
                
        except Exception as e:
            logging.error(f"Error processing event: {e}")
            return {'error': f'Processing error: {str(e)}'}
    
    def _process_schema_change(self, event: Dict[str, Any], change_data: Dict[str, Any], pipeline_id: int, pipeline_name: str) -> Dict[str, Any]:
        try:
            is_breaking = change_data.get('is_breaking', False)
            
            human_readable_message = SchemaChangeMessageGenerator.generate_human_readable_message(change_data)
            
            enhanced_change_data = change_data.copy()
            enhanced_change_data['human_readable_message'] = human_readable_message
            enhanced_change_data['pipeline_id'] = pipeline_id
            enhanced_change_data['pipeline_name'] = pipeline_name
            
            self._log_schema_change_event(pipeline_id, enhanced_change_data, is_breaking)            
            self._send_schema_change_notification(pipeline_id, pipeline_name, human_readable_message, change_data, is_breaking)
            
            if is_breaking:
                self._handle_breaking_change(pipeline_id)
            else:
                self._trigger_pipeline_for_schema_change(pipeline_id, change_data)
            
            return {
                'success': True,
                'pipeline_id': pipeline_id,
                'pipeline_name': pipeline_name,
                'change_data': enhanced_change_data,
                'is_breaking': is_breaking,
                'human_readable_message': human_readable_message,
                'timestamp': change_data.get('timestamp'),
                'transaction_id': change_data.get('transaction_id'),
                'change_category': change_data.get('change_category', 'other'),
                'command_tag': change_data.get('command_tag'),
                'object_identity': change_data.get('object_identity'),
                'schema_name': change_data.get('schema_name'),
                'command': change_data.get('command')
            }
            
        except Exception as e:
            logging.error(f"Error processing schema change for pipeline {pipeline_id}: {e}")
            return {'error': f'Schema change processing error: {str(e)}'}
    
    def _get_pipeline_name(self, pipeline_id: int) -> str:
        pipeline = self.pipeline_repo.get_pipline_by_id(pipeline_id)
        if pipeline:
            return getattr(pipeline, 'name', 'N/A')
        return "N/A"
    
    def _log_schema_change_event(self, pipeline_id: int, enhanced_change_data: Dict[str, Any], is_breaking: bool):
        try:
            change_type_enum = SchemaChangeTypeEnum.breaking if is_breaking else SchemaChangeTypeEnum.non_breaking
            payload_json = json.dumps(enhanced_change_data)
            
            self.schema_repository.add_event(
                pipeline_id=pipeline_id,
                change_type=change_type_enum,
                payload=payload_json
            )
        except Exception as e:
            print(f"Error logging schema change event: {e}")
    
    def _send_schema_change_notification(self, pipeline_id: int, pipeline_name: str, human_readable_message: str, 
                                       technical_details: Dict[str, Any], is_breaking: bool):
        try:
            notifier = PipelineEmailNotifier(
                pipeline_id=pipeline_id,
                pipeline_name=pipeline_name,
                human_readable_message=human_readable_message,
                technical_details=json.dumps(technical_details, indent=2),
                is_breaking=is_breaking
            )
            notifier.send_schema_change_notification()
        except Exception as e:
            print(f"Error sending schema change notification: {e}")
    
    def _handle_breaking_change(self, pipeline_id: int):
        try:
            result = self.pipeline_repo.update_pipeline_status(pipeline_id, "broken")
            
        except Exception as e:
            print(f"Error handling breaking change: {e}")
    
    def _trigger_pipeline_for_schema_change(self, pipeline_id: int, change_data: Dict[str, Any]):
        try:
            if self.schema_listener_manager:
                self.schema_listener_manager.execute_pipeline(pipeline_id)
                
        except Exception as e:
            print(f"Error triggering pipeline for schema change: {e}")
