import asyncio
import aiohttp
from typing import Dict
from source.config.config import keycloak_config

class KeycloakConnectionService:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.config = keycloak_config
    
    async def test_connection(self) -> Dict[str, bool]:
        try:
            if not self.session:
                return {"reachable": False, "error": "No session available"}
            
            # Test the health endpoint
            health_url = f"{self.config.server_url}/realms/master"
            async with self.session.get(health_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                return {"reachable": response.status == 200}
        except asyncio.TimeoutError:
            return {"reachable": False, "error": "Connection timeout"}
        except Exception as e:
            return {"reachable": False, "error": str(e)}
    
    async def wait_for_ready(self, max_attempts: int = 15, delay: float = 3.0) -> bool:
        for attempt in range(max_attempts):
            try:
                result = await self.test_connection()
                if result["reachable"]:
                    return True
                await asyncio.sleep(delay)
            except Exception as e:
                await asyncio.sleep(delay)
        return False