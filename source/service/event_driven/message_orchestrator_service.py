import logging
from typing import Dict, Any
from source.service.event_driven.kafka_service import KafkaService
from source.service.event_driven.message_processor_service import MessageProcessorService

logger = logging.getLogger(__name__)

class MessageOrchestratorService:
    
    def __init__(self):
        self.kafka_service = KafkaService()
        self.message_processor = MessageProcessorService()
        self._is_initialized = False
        
    async def initialize(self) -> bool:
        try:
            kafka_init = await self.kafka_service.initialize()
            processor_init = await self.message_processor.initialize()
            
            if all([kafka_init, processor_init]):
                self._is_initialized = True
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    async def start_consumer(self, pipeline_name: str, topic: str) -> Dict[str, Any]:
        try:
            if not self._is_initialized:
                return {"error": "Message Orchestrator service not initialized"}
            
            consumer_config = {
                "consumer_id": f"{pipeline_name}-consumer",
                "kafka_topic": topic,
                "group_id": f"{pipeline_name}-group",
                "auto_offset_reset": "latest"
            }
            
            message_handler = self._create_message_handler(pipeline_name)
            
            result = await self.kafka_service.start_consumer(
                consumer_config, 
                message_handler
            )
            
            if result.get("success"):
                return result
            else:
                return result
                
        except Exception as e:
            return {"error": f"Error starting consumer: {str(e)}"}
    
    def _create_message_handler(self, pipeline_name: str):
        async def message_handler(message_data: Dict[str, Any]):
            try:
                result = self.message_processor.process_message(message_data)
                
                if result.get("status") == "processed":
                    pass
                else:
                    pass
                    
            except Exception as e:
                pass
        
        return message_handler
    
    async def stop_consumer(self, consumer_id: str) -> Dict[str, Any]:
        return await self.kafka_service.stop_consumer(consumer_id)
    
    async def list_consumers(self) -> Dict[str, Any]:
        return await self.kafka_service.list_consumers()
    
    async def close(self) -> bool:
        try:
            await self.kafka_service.close()
            await self.message_processor.close()
            
            self._is_initialized = False
            return True
            
        except Exception as e:
            return False
    
    @property
    def is_initialized(self) -> bool:
        return self._is_initialized