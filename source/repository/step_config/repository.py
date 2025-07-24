from source.models.step_config.model import configuration 
from source.repository.database import get_db

database= get_db()

class configurationRepository:
    def __init__(self):
        self.db = database
    def get_all_step_configs(self):
        return (
            self.db.query(configuration).all()
        )
    def get_all_step_types(self):
        results = self.db.query(configuration.type).filter(configuration.is_deprecated == False).distinct().all()
        return [row[0] for row in results]

    def get_all_tools(self, type: str):
        results = self.db.query(configuration.tool).filter(
            configuration.is_deprecated == False,
            configuration.type == type
        ).distinct().all()
        return [row[0] for row in results]

    def get_all_tools_name(self):
        results = self.db.query(configuration.tool).filter(
            configuration.is_deprecated == False,
        ).distinct().all()
        return [row[0] for row in results]
    def get_step_config_per_tool(self,tool:str):
        return self.db.query(configuration).filter(
            configuration.tool == tool ).all() 
    
    def get_all_plugin_types(self, tool: str, type: str):
        results = self.db.query(configuration.plugin_type).filter(
            configuration.is_deprecated == False,
            configuration.type == type,
            configuration.tool == tool
        ).distinct().all()
        return [row[0] for row in results]
    
    def get_step_config_by_type_tool_plugin_type(self,type:str,tool:str,plugin_type:str):
        return self.db.query(configuration).filter(
            configuration.is_deprecated == False,
            configuration.plugin_type == plugin_type,
            configuration.tool == tool,
            configuration.type == type

        ).all()
    
    def get_by_id(self, step_config_id: int):
        return self.db.query(configuration).filter(configuration.step_config_id == step_config_id).first()

    def mark_deprecated(self, step_config_id: int):
        step_config = self.db.query(configuration).filter(configuration.step_config_id == step_config_id).first()
        if step_config:
            step_config.is_deprecated = True
            self.db.commit()
            self.db.refresh(step_config)
