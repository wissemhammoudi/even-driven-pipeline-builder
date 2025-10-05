import httpx
import logging
from typing import Dict, Any
from functools import wraps
from source.config.config import external_services_config

logger = logging.getLogger(__name__)

def handle_debezium_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error occurred: {e.response.text}"}
        except httpx.RequestError as e:
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    return wrapper

class DebeziumService:
    
    def __init__(self):
        self.connector_url = external_services_config.debezium_url
        self.session = None
        self._is_connected = False
        
    async def initialize(self) -> bool:
        try:
            self.session = httpx.AsyncClient(timeout=30.0)
            
            await self._test_connection()
            self._is_connected = True
            return True
            
        except Exception as e:
            self._is_connected = False
            return False
    
    async def _test_connection(self) -> bool:
        try:
            response = await self.session.get(f"{self.connector_url}/connectors")
            if response.status_code == 200:
                return True
            else:
                return False
                    
        except Exception as e:
            return False
    
    @handle_debezium_errors
    async def create_connector(self, connector_name: str, database_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        try:
            connector_classes = {
                "postgresql": "io.debezium.connector.postgresql.PostgresConnector",
                "mysql": "io.debezium.connector.mysql.MySqlConnector",
                "mongodb": "io.debezium.connector.mongodb.MongoDbConnector",
                "sqlserver": "io.debezium.connector.sqlserver.SqlServerConnector",
                "oracle": "io.debezium.connector.oracle.OracleConnector"
            }
            
            connector_class = connector_classes.get(database_type.lower())
            if not connector_class:
                return {"error": f"Unsupported database type: {database_type}"}
            
            connector_config = {
                "name": connector_name,
                "config": {
                    "connector.class": connector_class,
                    "database.server.name": config.get("database.server.name", connector_name),
                    "topic.prefix": config.get("topic.prefix", connector_name),
                    "database.server.id": config.get("database.server.id", "1"),
                    "schema.history.internal.kafka.bootstrap.servers": config.get("schema.history.internal.kafka.bootstrap.servers") or config.get("database.history.kafka.bootstrap.servers"),
                    "schema.history.internal.kafka.topic": config.get("schema.history.internal.kafka.topic") or config.get("database.history.kafka.topic", f"{connector_name}.dbhistory"),
                    "include.schema.changes": config.get("include.schema.changes", "true"),
                    # Start from current LSN/offset rather than beginning (for fresh connectors)
                    "snapshot.mode": config.get("snapshot.mode", "never")
                }
            }
            
            if database_type.lower() == "postgresql":
                connector_config["config"].update({
                    "database.hostname": config.get("database.hostname"),
                    "database.port": config.get("database.port", "5432"),
                    "database.user": config.get("database.user"),
                    "database.password": config.get("database.password"),
                    "database.dbname": config.get("database.dbname"),
                    "plugin.name": config.get("plugin.name", "pgoutput"),
                    "publication.autocreate.mode": config.get("publication.autocreate.mode", "filtered"),
                    "slot.drop.on.stop": config.get("slot.drop.on.stop", "true")
                })
            elif database_type.lower() == "mysql":
                connector_config["config"].update({
                    "database.hostname": config.get("database.hostname"),
                    "database.port": config.get("database.port", "3306"),
                    "database.user": config.get("database.user"),
                    "database.password": config.get("database.password"),
                    "database.server.id": config.get("database.server.id", "1"),
                    "database.include.list": config.get("database.include.list", ""),
                    "database.exclude.list": config.get("database.exclude.list", "")
                })
            elif database_type.lower() == "mongodb":
                connector_config["config"].update({
                    "mongodb.hosts": config.get("mongodb.hosts"),
                    "mongodb.user": config.get("mongodb.user"),
                    "mongodb.password": config.get("mongodb.password"),
                    "mongodb.name": config.get("mongodb.name")
                })
            elif database_type.lower() == "sqlserver":
                connector_config["config"].update({
                    "database.hostname": config.get("database.hostname"),
                    "database.port": config.get("database.port", "1433"),
                    "database.user": config.get("database.user"),
                    "database.password": config.get("database.password"),
                    "database.dbname": config.get("database.dbname")
                })
            elif database_type.lower() == "oracle":
                connector_config["config"].update({
                    "database.hostname": config.get("database.hostname"),
                    "database.port": config.get("database.port", "1521"),
                    "database.user": config.get("database.user"),
                    "database.password": config.get("database.password"),
                    "database.dbname": config.get("database.dbname")
                })
            
            request_body = connector_config
            safe_body = request_body.copy()
            try:
                if "config" in safe_body:
                    cfg = dict(safe_body["config"])
                    if "database.password" in cfg:
                        cfg["database.password"] = "***"
                    safe_body["config"] = cfg
            except Exception:
                pass

            check_response = await self.session.get(f"{self.connector_url}/connectors/{connector_name}")
            if check_response.status_code == 200:
                return {"result": check_response.json()}
            
            response = await self.session.post(
                f"{self.connector_url}/connectors",
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                json=connector_config
            )
            if response.status_code in [200, 201]:
                result = response.json()
                return {"result": result}
            elif response.status_code == 409:
                status_response = await self.session.get(f"{self.connector_url}/connectors/{connector_name}")
                if status_response.status_code == 200:
                    return {"result": status_response.json()}
                else:
                    error_text = status_response.text
            else:
                error_text = response.text
                try:
                    validate_resp = await self.session.put(
                        f"{self.connector_url}/connector-plugins/{connector_class}/config/validate",
                        headers={"Content-Type": "application/json", "Accept": "application/json"},
                        json=connector_config["config"]
                    )
                except Exception as _e:
                    pass
                return {"error": f"Failed to create {database_type} connector {connector_name}: {error_text}"}
                    
        except Exception as e:
            return {"error": f"Failed to create {database_type} connector {connector_name}: {str(e)}"}
    
    @handle_debezium_errors
    async def delete_connector(self, connector_name: str) -> Dict[str, Any]:
        try:
            response = await self.session.delete(
                f"{self.connector_url}/connectors/{connector_name}",
                headers={"Content-Type": "application/json", "Accept": "application/json"}
            )
            if response.status_code in [200, 204]:
                return {"result": f"Connector '{connector_name}' deleted successfully"}
            else:
                return {"error": f"Failed to delete connector {connector_name}: {response.status_code}"}
                    
        except Exception as e:
            return {"error": f"Failed to delete connector {connector_name}: {str(e)}"}
    
    async def close(self) -> bool:
        try:
            if self.session:
                await self.session.aclose()
                self.session = None
            
            self._is_connected = False
            return True
            
        except Exception as e:
            return False
    
    @property
    def is_connected(self) -> bool:
        return self._is_connected