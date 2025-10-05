import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import redis
from source.config.config import redis_config

logger = logging.getLogger(__name__)

class RedisService:
    
    def __init__(self):
        self.redis_host = redis_config.redis_host
        self.redis_port = redis_config.redis_port
        self.redis_password = getattr(redis_config, 'redis_password', None) or None
        self.redis_client = None
        self._is_connected = False
        
    async def initialize(self) -> bool:
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                db=0,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            await self._test_connection()
            self._is_connected = True
            return True
            
        except Exception as e:
            self._is_connected = False
            return False
    
    async def _test_connection(self) -> bool:
        try:
            result = self.redis_client.ping()
            if result:
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    def _generate_cache_key(self, prefix: str, identifier: str) -> str:
        return f"cache:{prefix}:{identifier}"
    
    async def set_cache_data(self, prefix: str, identifier: str, data: Any, 
                           expiry_seconds: int = 300) -> bool:
        try:
            if not self._is_connected:
                return False
            
            key = self._generate_cache_key(prefix, identifier)
            
            if isinstance(data, (dict, list)):
                data_json = json.dumps(data)
            else:
                data_json = str(data)
            
            self.redis_client.setex(key, expiry_seconds, data_json)
            return True
            
        except Exception as e:
            return False
    
    async def get_cache_data(self, prefix: str, identifier: str) -> Optional[Any]:
        try:
            if not self._is_connected:
                return None
            
            key = self._generate_cache_key(prefix, identifier)
            data = self.redis_client.get(key)
            
            if data:
                try:
                    result = json.loads(data)
                except json.JSONDecodeError:
                    result = data
                
                return result
            else:
                return None
                
        except Exception as e:
            return None
    
    async def delete_cache_data(self, prefix: str, identifier: str) -> bool:
        try:
            if not self._is_connected:
                return False
            
            key = self._generate_cache_key(prefix, identifier)
            result = self.redis_client.delete(key)
            
            if result:
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    async def close(self) -> bool:
        try:
            if self.redis_client:
                self.redis_client.close()
                self.redis_client = None
            
            self._is_connected = False
            return True
            
        except Exception as e:
            return False
    
    @property
    def is_connected(self) -> bool:
        return self._is_connected