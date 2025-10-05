from typing import Dict, Any, List, Tuple, Optional
from source.schema.pipeline.schema import StepTypeEnum

class PipelineConfigExtractor:
    def extract_db_config_and_schema_from_steps(self, step) -> Tuple[Optional[Dict], Optional[str]]:
        if not step:
            return None, None
        config = step.step_config
        conn_conf = config.get('connection_config', {})
        db_info = conn_conf.get('source') or conn_conf.get('extractor')
        if not db_info:
            db_info = conn_conf.get('destination_config')
        
        if db_info:
            try:
                db_config = {
                    'host': db_info['host'],
                    'dbname': db_info.get('database') or db_info.get('dbname'),
                    'user': db_info.get('username') or db_info.get('user'),
                    'password': db_info['password'],
                    'port': db_info['port'],
                }
                schema = config.get('target_schema') or db_info.get('schema') or config.get('schema')
                return db_config, schema
            except Exception as e:
                print(f"Error extracting DB config from connection_config: {e}")
                return None, None
        if all(k in config for k in ['host', 'dbname', 'user', 'password', 'port', 'schema']):
            db_config = {
                'host': config['host'],
                'dbname': config['dbname'],
                'user': config['user'],
                'password': config['password'],
                'port': config['port'],
            }
            schema = config['schema']
            return db_config, schema
            
        return None, None
    
    def extract_schema_change_tool_from_steps(self, step) -> str:
        config = step.step_config
        return config.get('schema_change_tool', 'postgresql').lower()
    
    def extract_tables_to_monitor_from_steps(self, step) -> List[str]:
        step_config = step.step_config
        if 'table_sync_config' in step_config:
            table_config = step_config['table_sync_config']
            if isinstance(table_config, list):
                return list(set(table_config))
            elif isinstance(table_config, dict):
                if "tables" in table_config:
                    tables = table_config["tables"]
                    if isinstance(tables, list):
                        return list(set(tables))
                    elif isinstance(tables, str):
                        return [tables]
                elif "table_name" in table_config:
                    return [table_config["table_name"]]
                else:
                    return list(set(table_config.keys()))
        
        return []
    
    def find_data_ingestion_step(self, steps) -> Optional[Any]:
        for step in steps:
            if step.step_config.get("config_type") == StepTypeEnum.DATA_INGESTION:
                return step
        return None
    
    def find_data_transformation_step(self, steps) -> Optional[Any]:
        for step in steps:
            if step.step_config.get("config_type") == StepTypeEnum.DATA_TRANSFORMATION:
                return step
        return None
    
    def select_primary_step(self, steps) -> Optional[Any]:
        if not steps:
            return None
            
        ingestion_step = self.find_data_ingestion_step(steps)
        if ingestion_step:
            return ingestion_step
        
        transformation_step = self.find_data_transformation_step(steps)
        if transformation_step:
            return transformation_step
        
        return steps[0] 