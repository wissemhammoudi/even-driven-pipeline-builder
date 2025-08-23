from typing import List, Optional
from source.models.user.models import User
from source.models.pipeline.models import Pipeline
from source.models.user_pipeline_access.model import UserPipelineAccess
from source.repository.database import get_db
from sqlalchemy import func
database= get_db()

class PipelineRepository:
    def __init__(self):
        self.db = database

    def get_paginated_pipelines(self, offset: int = 0, limit: int = 10, deprecated: bool = False, name: str = None, created_date=None, user_id: Optional[str] = None):
        if user_id is not None:
            query = self.db.query(Pipeline).join(
                UserPipelineAccess, 
                Pipeline.pipeline_id == UserPipelineAccess.pipeline_id
            ).filter(
                Pipeline.is_deleted == False,
                UserPipelineAccess.user_id == user_id
            )
        else:
            query = self.db.query(Pipeline).filter(Pipeline.is_deleted == False)
        
        if deprecated is not None:
            query = query.filter(Pipeline.is_deprecated == deprecated)
        if name:
            query = query.filter(Pipeline.name.ilike(f"%{name}%"))
        if created_date:
            query = query.filter(func.date(Pipeline.created_at) == created_date)
        
        total_count = query.count()  
        pipelines = query.offset(offset).limit(limit).all()
        
        return pipelines, total_count
    
    def get_all_pipelines_ids(self) -> List[int]:
        pipelines = self.db.query(Pipeline).filter(Pipeline.is_deleted == False)
        return [pipeline.pipeline_id for pipeline in pipelines]
    
    def get_active_pipeline_by_user_id(self,user_id: str) -> List[Pipeline]:
        return self.db.query(Pipeline).filter(
            Pipeline.created_by == user_id,
            Pipeline.is_deleted == False
            ).all()

    def get_Active_Pipeline_by_id(self,pipeline_id: int) -> Optional[Pipeline]:
        return self.db.query(Pipeline).filter(
            Pipeline.pipeline_id == pipeline_id,
            Pipeline.is_deleted == False
            ).first()
    
    def get_pipline_by_id(self,pipeline_id:int):
        return self.db.query(Pipeline).filter(Pipeline.pipeline_id==pipeline_id,Pipeline.is_deleted == False).first()
    
    def create_Pipeline(self,pipeline: Pipeline):
        try:
            self.db.add(pipeline)
            self.db.commit()
            self.db.refresh(pipeline) 
            id=pipeline.pipeline_id       
            return id
        except Exception as e:
            self.db.rollback()
            raise e

    def mark_pipeline_deleted(self,pipeline:Pipeline):
        try:
            pipeline.is_deleted = True
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        
    def mark_deprecated(self, pipeline_id: int):
        try:
            pipeline = self.db.query(Pipeline).filter(Pipeline.pipeline_id == pipeline_id).first()
            if pipeline:
                pipeline.is_deprecated = True
                self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
            
    def get_user_by_id(self,user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.user_id == user_id).first()
    
    def rollback(self):
        self.db.rollback()

    def commit(self):
        self.db.commit()