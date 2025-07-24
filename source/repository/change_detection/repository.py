from source.models.change_detection.models import SchemaChangeEvent, SchemaChangeTypeEnum
from source.repository.database import get_db

class SchemaChangeRepository:
    def __init__(self):
        self.db = get_db()

    def add_event(self, pipeline_id, change_type, payload):
        event = SchemaChangeEvent(
            pipeline_id=pipeline_id,
            change_type=change_type,
            payload=payload
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_events_by_pipeline(self, pipeline_id):
        return self.db.query(SchemaChangeEvent).filter(SchemaChangeEvent.pipeline_id == pipeline_id).all()

    def get_all_events(self):
        return self.db.query(SchemaChangeEvent).all() 