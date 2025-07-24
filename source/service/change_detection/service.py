from source.repository.change_detection.repository import SchemaChangeRepository
from source.schema.change_detection.schema import SchemaChangeTypeEnum
from typing import List

class ChangeDetectionService:
    def __init__(self):
        self.repository = SchemaChangeRepository()
    
    def _extract_human_readable_message(self, payload: str) -> str:
        try:
            import json
            payload_data = json.loads(payload)
            return payload_data.get('human_readable_message', 'Schema change detected')
        except:
            return 'Schema change detected'
    
    def log_schema_change(self, pipeline_id: int, change_data: dict, is_breaking: bool) -> bool:

        try:
            import json
            change_type = SchemaChangeTypeEnum.breaking if is_breaking else SchemaChangeTypeEnum.non_breaking
            payload_json = json.dumps(change_data)
            
            self.repository.add_event(
                pipeline_id=pipeline_id,
                change_type=change_type,
                payload=payload_json
            )
            return True
        except Exception as e:
            print(f"Failed to log schema change event: {e}")
            return False
    
    def get_schema_changes_by_pipeline(self, pipeline_id: int) -> List[dict]:

        try:
            events = self.repository.get_events_by_pipeline(pipeline_id)
            return [
                {
                    'id': event.id,
                    'pipeline_id': event.pipeline_id,
                    'event_time': event.event_time,
                    'change_type': event.change_type.value,
                    'payload': event.payload,
                    'human_readable_message': self._extract_human_readable_message(event.payload)
                }
                for event in events
            ]
        except Exception as e:
            print(f"Failed to get schema changes for pipeline {pipeline_id}: {e}")
            return []
    
    def get_all_schema_changes(self) -> List[dict]:

        try:
            events = self.repository.get_all_events()
            return [
                {
                    'id': event.id,
                    'pipeline_id': event.pipeline_id,
                    'event_time': event.event_time,
                    'change_type': event.change_type.value,
                    'payload': event.payload,
                    'human_readable_message': self._extract_human_readable_message(event.payload)
                }
                for event in events
            ]
        except Exception as e:
            print(f"Failed to get all schema changes: {e}")
            return []
    
    def get_breaking_changes_by_pipeline(self, pipeline_id: int) -> List[dict]:
 
        try:
            events = self.repository.get_events_by_pipeline(pipeline_id)
            breaking_events = [
                event for event in events 
                if event.change_type == SchemaChangeTypeEnum.breaking
            ]
            return [
                {
                    'id': event.id,
                    'pipeline_id': event.pipeline_id,
                    'event_time': event.event_time,
                    'change_type': event.change_type.value,
                    'payload': event.payload,
                    'human_readable_message': self._extract_human_readable_message(event.payload)
                }
                for event in breaking_events
            ]
        except Exception as e:
            print(f"Failed to get breaking changes for pipeline {pipeline_id}: {e}")
            return [] 