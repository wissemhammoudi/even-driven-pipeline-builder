import asyncio
import json
import logging
import threading
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timezone
from confluent_kafka import Producer, Consumer, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic, ConfigResource, ResourceType
from source.config.config import external_services_config

logger = logging.getLogger(__name__)

class KafkaService:
    
    def __init__(self):
        self.bootstrap_servers = external_services_config.kafka_bootstrap_servers
        self.producer = None
        self.admin_client = None
        self.consumers = {}
        self.consumers_lock = threading.Lock()
        self._is_connected = False
        
    async def initialize(self) -> bool:
        try:
            self.producer = Producer({
                'bootstrap.servers': self.bootstrap_servers,
                'acks': 'all',
                'retries': 3,
                'max.in.flight.requests.per.connection': 1
            })
            
            self.admin_client = AdminClient({
                'bootstrap.servers': self.bootstrap_servers
            })
            
            await self._test_connection()
            self._is_connected = True
            return True
            
        except Exception as e:
            self._is_connected = False
            return False
    
    async def _test_connection(self) -> bool:
        try:
            test_producer = Producer({'bootstrap.servers': self.bootstrap_servers})
            metadata = test_producer.list_topics(timeout=10)
            test_producer.flush()
            return True
            
        except Exception as e:
            return False
    
    async def get_topic_info(self, topic_name: str) -> Dict[str, Any]:
        try:
            if not self._is_connected or not self.admin_client:
                return {"error": "Kafka admin client not initialized"}
            
            metadata = self.admin_client.list_topics(timeout=10)
            
            if topic_name not in metadata.topics:
                return {"error": f"Topic '{topic_name}' not found"}
            
            topic_metadata = metadata.topics[topic_name]
            
            return {
                "success": True,
                "topic_name": topic_name,
                "partitions": len(topic_metadata.partitions),
                "replication_factor": len(topic_metadata.partitions[0].replicas) if topic_metadata.partitions else 0,
                "error": topic_metadata.error
            }
            
        except Exception as e:
            return {"error": f"Error getting topic info: {str(e)}"}
    
    async def list_topics(self) -> Dict[str, Any]:
        try:
            if not self._is_connected or not self.producer:
                return {"error": "Kafka service not connected"}
            
            metadata = self.producer.list_topics(timeout=10)
            topics = list(metadata.topics.keys())
            
            return {
                "success": True,
                "topics": topics,
                "total_count": len(topics)
            }
            
        except Exception as e:
            return {"error": f"Error listing topics: {str(e)}"}
    
    async def start_consumer(self, consumer_config: Dict[str, Any], message_handler: Callable) -> Dict[str, Any]:
        try:
            consumer_id = consumer_config.get("consumer_id")
            topic = consumer_config.get("kafka_topic")
            group_id = consumer_config.get("group_id", f"{consumer_id}-group")
            auto_offset_reset = consumer_config.get("auto_offset_reset", "earliest")
            
            with self.consumers_lock:
                if consumer_id in self.consumers:
                    return {"error": f"Consumer '{consumer_id}' already running"}
                
                consumer = Consumer({
                    'bootstrap.servers': self.bootstrap_servers,
                    'group.id': group_id,
                    'auto.offset.reset': auto_offset_reset,
                    'enable.auto.commit': True
                })
                
                self.consumers[consumer_id] = {
                    'consumer': consumer,
                    'running': True,
                    'topic': topic,
                    'thread': None
                }
                
                thread = threading.Thread(
                    target=self._message_consumption_loop,
                    args=(consumer_id, topic, message_handler),
                    daemon=True
                )
                self.consumers[consumer_id]['thread'] = thread
                thread.start()
                
                return {
                    "success": True,
                    "consumer_id": consumer_id,
                    "topic": topic,
                    "message": f"Consumer '{consumer_id}' started successfully"
                }
                
        except Exception as e:
            return {"error": f"Error starting consumer: {str(e)}"}
    
    def _message_consumption_loop(self, consumer_id: str, topic: str, message_handler: Callable):
        consumer = self.consumers[consumer_id]['consumer']
        consumer.subscribe([topic])
        
        poll_count = 0
        try:
            while self.consumers[consumer_id]['running']:
                poll_count += 1
                
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                
                if msg.error():
                    self._handle_kafka_error(msg.error(), topic)
                    continue
                
                try:
                    message_data = {
                        'topic': msg.topic(),
                        'partition': msg.partition(),
                        'offset': msg.offset(),
                        'key': msg.key().decode('utf-8') if msg.key() else None,
                        'value': json.loads(msg.value().decode('utf-8')) if msg.value() else None,
                        'timestamp': msg.timestamp()
                    }
                    
                    try:
                        loop = asyncio.get_running_loop()
                        loop.call_soon_threadsafe(
                            asyncio.create_task,
                            self._handle_message_async(message_handler, message_data)
                        )
                    except RuntimeError:
                        if asyncio.iscoroutinefunction(message_handler):
                            def _run_coro():
                                new_loop = asyncio.new_event_loop()
                                try:
                                    asyncio.set_event_loop(new_loop)
                                    new_loop.run_until_complete(
                                        self._handle_message_async(message_handler, message_data)
                                    )
                                finally:
                                    new_loop.close()
                            threading.Thread(target=_run_coro, daemon=True).start()
                        else:
                            message_handler(message_data)
                    
                except Exception as e:
                    pass
                    
        except Exception as e:
            pass
        finally:
            consumer.close()
            self._mark_consumer_stopped(consumer_id)
    
    async def _handle_message_async(self, message_handler: Callable, message_data: Dict[str, Any]):
        try:
            if asyncio.iscoroutinefunction(message_handler):
                result = await message_handler(message_data)
            else:
                result = message_handler(message_data)
        except Exception as e:
            pass
    
    def _handle_kafka_error(self, error: KafkaError, topic: str):
        pass
    
    def _mark_consumer_stopped(self, consumer_id: str):
        with self.consumers_lock:
            if consumer_id in self.consumers:
                self.consumers[consumer_id]['running'] = False
    
    async def stop_consumer(self, consumer_id: str) -> Dict[str, Any]:
        try:
            with self.consumers_lock:
                if consumer_id not in self.consumers:
                    return {"error": f"Consumer '{consumer_id}' not running"}
                
                consumer_data = self.consumers.pop(consumer_id)
                consumer_data['running'] = False
                consumer_data['consumer'].close()
                
                if consumer_data['thread'] and consumer_data['thread'].is_alive():
                    consumer_data['thread'].join(timeout=5)
                
                return {
                    "success": True,
                    "message": f"Consumer '{consumer_id}' stopped successfully"
                }
                
        except Exception as e:
            return {"error": f"Error stopping consumer: {str(e)}"}
    
    async def get_consumer_info(self, consumer_id: str) -> Dict[str, Any]:
        try:
            with self.consumers_lock:
                consumer_info = self.consumers.get(consumer_id)
            
            if not consumer_info:
                return {"error": f"Consumer '{consumer_id}' not running"}
            
            return {
                "success": True,
                "consumer_id": consumer_id,
                "topic": consumer_info['topic'],
                "running": consumer_info['running'],
                "thread_status": "running" if consumer_info['running'] else "stopped"
            }
            
        except Exception as e:
            return {"error": f"Error getting consumer info: {str(e)}"}
    
    async def list_consumers(self) -> Dict[str, Any]:
        try:
            with self.consumers_lock:
                if not self.consumers:
                    return {"success": True, "consumers": [], "total_count": 0}
                
                consumers = []
                for consumer_id, data in self.consumers.items():
                    consumers.append({
                        "consumer_id": consumer_id,
                        "topic": data["topic"],
                        "running": data["running"],
                        "thread_status": "running" if data["running"] else "stopped"
                    })
                
                return {
                    "success": True,
                    "consumers": consumers,
                    "total_count": len(consumers)
                }
                
        except Exception as e:
            return {"error": f"Error listing consumers: {str(e)}"}
    
    async def close(self) -> bool:
        try:
            with self.consumers_lock:
                for consumer_id in list(self.consumers.keys()):
                    await self.stop_consumer(consumer_id)
            
            if self.producer:
                self.producer.flush()
                self.producer = None
            
            if self.admin_client:
                self.admin_client = None
            
            self._is_connected = False
            return True
            
        except Exception as e:
            return False
    
    @property
    def is_connected(self) -> bool:
        return self._is_connected
    
    @property
    def kafka_broker(self) -> str:
        return self.bootstrap_servers

    async def create_consumer(self, consumer_id: str, topic: str, group_id: Optional[str] = None, auto_offset_reset: str = "earliest") -> Dict[str, Any]:
        try:
            with self.consumers_lock:
                if consumer_id in self.consumers:
                    return {"error": f"Consumer '{consumer_id}' already exists"}

                consumer = Consumer({
                    'bootstrap.servers': self.bootstrap_servers,
                    'group.id': group_id or f"{consumer_id}-group",
                    'auto.offset.reset': auto_offset_reset,
                    'enable.auto.commit': True
                })

                self.consumers[consumer_id] = {
                    'consumer': consumer,
                    'running': False,
                    'topic': topic,
                    'thread': None
                }

            return {
                "success": True,
                "consumer_id": consumer_id,
                "topic": topic,
                "consumer": consumer,
                "message": f"Consumer '{consumer_id}' created"
            }
        except Exception as e:
            return {"error": f"Error creating consumer: {str(e)}"}

    async def start_consuming(self, consumer_id: str, message_handler: Callable) -> Dict[str, Any]:
        try:
            with self.consumers_lock:
                if consumer_id not in self.consumers:
                    return {"error": f"Consumer '{consumer_id}' not found"}
                if self.consumers[consumer_id]['running']:
                    return {"error": f"Consumer '{consumer_id}' already running"}

                topic = self.consumers[consumer_id]['topic']

                thread = threading.Thread(
                    target=self._message_consumption_loop,
                    args=(consumer_id, topic, message_handler),
                    daemon=True
                )
                self.consumers[consumer_id]['running'] = True
                self.consumers[consumer_id]['thread'] = thread
                thread.start()

            return {"success": True, "consumer_id": consumer_id, "topic": topic}
        except Exception as e:
            return {"error": f"Error starting consuming: {str(e)}"}

    async def stop_consuming(self, consumer_id: str) -> Dict[str, Any]:
        try:
            with self.consumers_lock:
                data = self.consumers.get(consumer_id)
                if not data:
                    return {"error": f"Consumer '{consumer_id}' not found"}
                if not data['running']:
                    return {"success": True, "message": f"Consumer '{consumer_id}' already stopped"}
                data['running'] = False
                thread = data.get('thread')

            if thread and thread.is_alive():
                thread.join(timeout=5)

            return {"success": True}
        except Exception as e:
            return {"error": f"Error stopping consuming: {str(e)}"}