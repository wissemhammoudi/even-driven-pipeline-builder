import requests
import json
import logging
from typing import Dict, Any, Optional, List
from source.config.config import debezium_config
from source.models.schema_change import SchemaChangeEvent, DebeziumChangeEvent
import uuid

logger = logging.getLogger(__name__)

class DebeziumService:
    def __init__(self):
        self.base_url = debezium_config.debezium_url
        self.connector_name = debezium_config.debezium_connector_name
        
    def create_postgres_connector(self) -> Dict[str, Any]:
        """Create a PostgreSQL connector for Debezium"""
        connector_config = {
            "name": self.connector_name,
            "config": {
                "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
                "database.hostname": debezium_config.debezium_database_hostname,
                "database.port": debezium_config.debezium_database_port,
                "database.user": debezium_config.debezium_database_user,
                "database.password": debezium_config.debezium_database_password,
                "database.dbname": debezium_config.debezium_database_dbname,
                "database.server.name": debezium_config.debezium_database_server_name,
                "topic.prefix": debezium_config.debezium_topic_prefix,
                "schema.include.list": debezium_config.debezium_schema_include_list,
                "table.include.list": debezium_config.debezium_table_include_list,
                "plugin.name": "pgoutput",
                "publication.autocreate.mode": "filtered",
                "slot.name": "debezium_slot",
                "database.history.kafka.bootstrap.servers": "kafka:9092",
                "database.history.kafka.topic": f"{self.connector_name}.dbhistory",
                "include.schema.changes": "true",
                "transforms": "unwrap",
                "transforms.unwrap.type": "io.debezium.transforms.ExtractNewDocumentState",
                "transforms.unwrap.drop.tombstones": "false",
                "transforms.unwrap.delete.handling.mode": "rewrite",
                "transforms.unwrap.operation.header": "true"
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/connectors",
                headers={"Content-Type": "application/json"},
                json=connector_config
            )
            
            if response.status_code == 201:
                logger.info(f"PostgreSQL connector '{self.connector_name}' created successfully")
                return response.json()
            else:
                logger.error(f"Failed to create connector: {response.status_code} - {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"Error creating PostgreSQL connector: {str(e)}")
            return {"error": str(e)}
    
    def get_connector_status(self, connector_name: Optional[str] = None) -> Dict[str, Any]:
        """Get the status of a specific connector"""
        connector = connector_name or self.connector_name
        
        try:
            response = requests.get(f"{self.base_url}/connectors/{connector}/status")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get connector status: {response.status_code}")
                return {"error": "Failed to get connector status"}
                
        except Exception as e:
            logger.error(f"Error getting connector status: {str(e)}")
            return {"error": str(e)}
    
    def get_all_connectors(self) -> List[Dict[str, Any]]:
        """Get all available connectors"""
        try:
            response = requests.get(f"{self.base_url}/connectors")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get connectors: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting connectors: {str(e)}")
            return []
    
    def delete_connector(self, connector_name: Optional[str] = None) -> Dict[str, Any]:
        """Delete a specific connector"""
        connector = connector_name or self.connector_name
        
        try:
            response = requests.delete(f"{self.base_url}/connectors/{connector}")
            
            if response.status_code == 204:
                logger.info(f"Connector '{connector}' deleted successfully")
                return {"success": True, "message": f"Connector '{connector}' deleted"}
            else:
                logger.error(f"Failed to delete connector: {response.status_code}")
                return {"error": "Failed to delete connector"}
                
        except Exception as e:
            logger.error(f"Error deleting connector: {str(e)}")
            return {"error": str(e)}
    
    def restart_connector(self, connector_name: Optional[str] = None) -> Dict[str, Any]:
        """Restart a specific connector"""
        connector = connector_name or self.connector_name
        
        try:
            response = requests.post(f"{self.base_url}/connectors/{connector}/restart")
            
            if response.status_code == 204:
                logger.info(f"Connector '{connector}' restarted successfully")
                return {"success": True, "message": f"Connector '{connector}' restarted"}
            else:
                logger.error(f"Failed to restart connector: {response.status_code}")
                return {"error": "Failed to restart connector"}
                
        except Exception as e:
            logger.error(f"Error restarting connector: {str(e)}")
            return {"error": str(e)}
    
    def get_connector_config(self, connector_name: Optional[str] = None) -> Dict[str, Any]:
        """Get the configuration of a specific connector"""
        connector = connector_name or self.connector_name
        
        try:
            response = requests.get(f"{self.base_url}/connectors/{connector}/config")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get connector config: {response.status_code}")
                return {"error": "Failed to get connector config"}
                
        except Exception as e:
            logger.error(f"Error getting connector config: {str(e)}")
            return {"error": str(e)}
    
    def update_connector_config(self, config: Dict[str, Any], connector_name: Optional[str] = None) -> Dict[str, Any]:
        """Update the configuration of a specific connector"""
        connector = connector_name or self.connector_name
        
        try:
            response = requests.put(
                f"{self.base_url}/connectors/{connector}/config",
                headers={"Content-Type": "application/json"},
                json=config
            )
            
            if response.status_code == 200:
                logger.info(f"Connector '{connector}' configuration updated successfully")
                return response.json()
            else:
                logger.error(f"Failed to update connector config: {response.status_code}")
                return {"error": "Failed to update connector config"}
                
        except Exception as e:
            logger.error(f"Error updating connector config: {str(e)}")
            return {"error": str(e)}
    
    def pause_connector(self, connector_name: Optional[str] = None) -> Dict[str, Any]:
        """Pause a specific connector"""
        connector = connector_name or self.connector_name
        
        try:
            response = requests.put(f"{self.base_url}/connectors/{connector}/pause")
            
            if response.status_code == 202:
                logger.info(f"Connector '{connector}' paused successfully")
                return {"success": True, "message": f"Connector '{connector}' paused"}
            else:
                logger.error(f"Failed to pause connector: {response.status_code}")
                return {"error": "Failed to pause connector"}
                
        except Exception as e:
            logger.error(f"Error pausing connector: {str(e)}")
            return {"error": str(e)}
    
    def resume_connector(self, connector_name: Optional[str] = None) -> Dict[str, Any]:
        """Resume a specific connector"""
        connector = connector_name or self.connector_name
        
        try:
            response = requests.put(f"{self.base_url}/connectors/{connector}/resume")
            
            if response.status_code == 202:
                logger.info(f"Connector '{connector}' resumed successfully")
                return {"success": True, "message": f"Connector '{connector}' resumed"}
            else:
                logger.error(f"Failed to resume connector: {response.status_code}")
                return {"error": "Failed to resume connector"}
                
        except Exception as e:
            logger.error(f"Error resuming connector: {str(e)}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the Debezium Connect service"""
        try:
            response = requests.get(f"{self.base_url}")
            
            if response.status_code == 200:
                return {"status": "healthy", "message": "Debezium Connect is running"}
            else:
                return {"status": "unhealthy", "message": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}
