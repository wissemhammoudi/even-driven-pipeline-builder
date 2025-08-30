import json
import logging
import asyncio
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from source.config.config import kafka_config, redis_config
from source.models.schema_change import SchemaChangeEvent, DebeziumChangeEvent, SchemaChangeNotification
from source.service.schema_change_detector import SchemaChangeDetector
import redis
import uuid

logger = logging.getLogger(__name__)

class KafkaConsumerService:
    def __init__(self):
        self.consumer = None
        self.producer = None
        self.redis_client = None
        self.schema_detector = SchemaChangeDetector()
        self.is_running = False
        self.event_handlers: List[Callable] = []
        
        # Initialize Redis connection
        self._init_redis()
        
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=redis_config.redis_host,
                port=redis_config.redis_port,
                db=redis_config.redis_db,
                password=redis_config.redis_password,
                decode_responses=redis_config.redis_decode_responses
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self.redis_client = None
    
    def _init_kafka_consumer(self, topic: str):
        """Initialize Kafka consumer"""
        try:
            self.consumer = KafkaConsumer(
                topic,
                bootstrap_servers=kafka_config.kafka_bootstrap_servers,
                group_id=kafka_config.kafka_consumer_group_id,
                auto_offset_reset=kafka_config.kafka_auto_offset_reset,
                enable_auto_commit=kafka_config.kafka_enable_auto_commit,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
                key_deserializer=lambda x: x.decode('utf-8') if x else None
            )
            logger.info(f"Kafka consumer initialized for topic: {topic}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {str(e)}")
            raise
    
    def _init_kafka_producer(self):
        """Initialize Kafka producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=kafka_config.kafka_bootstrap_servers,
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                key_serializer=lambda x: x.encode('utf-8') if x else None
            )
            logger.info("Kafka producer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {str(e)}")
            raise
    
    def add_event_handler(self, handler: Callable[[SchemaChangeEvent], None]):
        """Add an event handler for schema change events"""
        self.event_handlers.append(handler)
        logger.info(f"Event handler added. Total handlers: {len(self.event_handlers)}")
    
    def remove_event_handler(self, handler: Callable[[SchemaChangeEvent], None]):
        """Remove an event handler"""
        if handler in self.event_handlers:
            self.event_handlers.remove(handler)
            logger.info(f"Event handler removed. Total handlers: {len(self.event_handlers)}")
    
    def start_consuming(self, topic: str, auto_start: bool = True):
        """Start consuming messages from Kafka topic"""
        try:
            self._init_kafka_consumer(topic)
            self._init_kafka_producer()
            
            if auto_start:
                self.is_running = True
                self._consume_messages()
            
            logger.info(f"Started consuming from topic: {topic}")
            
        except Exception as e:
            logger.error(f"Failed to start consuming: {str(e)}")
            raise
    
    def stop_consuming(self):
        """Stop consuming messages"""
        self.is_running = False
        if self.consumer:
            self.consumer.close()
        if self.producer:
            self.producer.close()
        logger.info("Kafka consumer stopped")
    
    def _consume_messages(self):
        """Consume messages from Kafka topic"""
        try:
            for message in self.consumer:
                if not self.is_running:
                    break
                
                try:
                    # Process the message
                    self._process_message(message)
                    
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    # Continue processing other messages
                    continue
                    
        except Exception as e:
            logger.error(f"Error in message consumption loop: {str(e)}")
        finally:
            self.stop_consuming()
    
    def _process_message(self, message):
        """Process a single Kafka message"""
        try:
            # Extract message data
            value = message.value
            key = message.key
            topic = message.topic
            partition = message.partition
            offset = message.offset
            timestamp = message.timestamp
            
            logger.debug(f"Processing message: topic={topic}, partition={partition}, offset={offset}")
            
            # Check if this is a Debezium event
            if self._is_debezium_event(value):
                # Process as Debezium event
                schema_change_event = self._process_debezium_event(value, message)
                if schema_change_event:
                    self._handle_schema_change_event(schema_change_event)
            else:
                # Process as regular message
                self._process_regular_message(value, message)
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
    
    def _is_debezium_event(self, message_value: Any) -> bool:
        """Check if a message is a Debezium event"""
        if isinstance(message_value, dict):
            # Look for Debezium-specific fields
            return any(key in message_value for key in ['before', 'after', 'source', 'op'])
        return False
    
    def _process_debezium_event(self, event_data: Dict[str, Any], message) -> Optional[SchemaChangeEvent]:
        """Process a Debezium change event"""
        try:
            # Use schema detector to process the event
            schema_change_event = self.schema_detector.process_debezium_event(event_data)
            
            if schema_change_event:
                # Add metadata from the Kafka message
                schema_change_event.event_id = str(uuid.uuid4())
                schema_change_event.timestamp = datetime.fromtimestamp(message.timestamp / 1000.0)
                
                # Store in Redis for caching
                self._cache_schema_change_event(schema_change_event)
                
                logger.info(f"Schema change event processed: {schema_change_event.change_type} on {schema_change_event.table_name}")
            
            return schema_change_event
            
        except Exception as e:
            logger.error(f"Error processing Debezium event: {str(e)}")
            return None
    
    def _process_regular_message(self, message_value: Any, message):
        """Process a regular (non-Debezium) message"""
        try:
            logger.info(f"Processing regular message: {message_value}")
            # Add your custom logic for processing regular messages here
            
        except Exception as e:
            logger.error(f"Error processing regular message: {str(e)}")
    
    def _handle_schema_change_event(self, event: SchemaChangeEvent):
        """Handle a schema change event by calling all registered handlers"""
        try:
            # Create notification
            notification = SchemaChangeNotification(
                event_type="schema_change",
                table_name=event.table_name,
                schema_name=event.schema_name,
                change_type=event.change_type,
                change_details=event.change_details,
                timestamp=event.timestamp,
                event_id=event.event_id
            )
            
            # Call all registered handlers
            for handler in self.event_handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {str(e)}")
            
            # Publish to notification topic if needed
            self._publish_notification(notification)
            
            # Trigger any automated responses
            self._trigger_automated_responses(event)
            
        except Exception as e:
            logger.error(f"Error handling schema change event: {str(e)}")
    
    def _cache_schema_change_event(self, event: SchemaChangeEvent):
        """Cache schema change event in Redis"""
        if not self.redis_client:
            return
        
        try:
            # Cache the event with TTL (e.g., 24 hours)
            cache_key = f"schema_change:{event.event_id}"
            cache_data = {
                "table_name": event.table_name,
                "schema_name": event.schema_name,
                "change_type": event.change_type,
                "change_details": event.change_details,
                "timestamp": event.timestamp.isoformat(),
                "source_connector": event.source_connector
            }
            
            self.redis_client.setex(
                cache_key,
                86400,  # 24 hours TTL
                json.dumps(cache_data)
            )
            
            # Also cache by table for quick lookup
            table_cache_key = f"table_changes:{event.schema_name}.{event.table_name}"
            self.redis_client.lpush(table_cache_key, event.event_id)
            self.redis_client.expire(table_cache_key, 86400)
            
            logger.debug(f"Schema change event cached: {cache_key}")
            
        except Exception as e:
            logger.error(f"Error caching schema change event: {str(e)}")
    
    def _publish_notification(self, notification: SchemaChangeNotification):
        """Publish notification to Kafka topic"""
        if not self.producer:
            return
        
        try:
            topic = "schema-change-notifications"
            key = f"{notification.schema_name}.{notification.table_name}"
            
            self.producer.send(
                topic,
                key=key,
                value=notification.dict()
            )
            
            logger.debug(f"Notification published to topic: {topic}")
            
        except Exception as e:
            logger.error(f"Error publishing notification: {str(e)}")
    
    def _trigger_automated_responses(self, event: SchemaChangeEvent):
        """Trigger automated responses based on schema change type"""
        try:
            if event.change_type == "CREATE":
                self._handle_table_creation(event)
            elif event.change_type == "ALTER":
                self._handle_table_modification(event)
            elif event.change_type == "DROP":
                self._handle_table_dropping(event)
                
        except Exception as e:
            logger.error(f"Error triggering automated responses: {str(e)}")
    
    def _handle_table_creation(self, event: SchemaChangeEvent):
        """Handle table creation events"""
        logger.info(f"Table created: {event.schema_name}.{event.table_name}")
        # Add your logic for handling table creation
        # e.g., update documentation, notify data engineers, etc.
    
    def _handle_table_modification(self, event: SchemaChangeEvent):
        """Handle table modification events"""
        logger.info(f"Table modified: {event.schema_name}.{event.table_name}")
        # Add your logic for handling table modifications
        # e.g., validate data compatibility, update downstream systems, etc.
    
    def _handle_table_dropping(self, event: SchemaChangeEvent):
        """Handle table dropping events"""
        logger.info(f"Table dropped: {event.schema_name}.{event.table_name}")
        # Add your logic for handling table dropping
        # e.g., backup data, notify stakeholders, etc.
    
    def get_cached_events(self, table_name: str, schema_name: str = "public", limit: int = 10) -> List[Dict[str, Any]]:
        """Get cached schema change events for a specific table"""
        if not self.redis_client:
            return []
        
        try:
            cache_key = f"table_changes:{schema_name}.{table_name}"
            event_ids = self.redis_client.lrange(cache_key, 0, limit - 1)
            
            events = []
            for event_id in event_ids:
                event_key = f"schema_change:{event_id}"
                event_data = self.redis_client.get(event_key)
                if event_data:
                    events.append(json.loads(event_data))
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting cached events: {str(e)}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the Kafka consumer service"""
        health_status = {
            "status": "healthy",
            "kafka_consumer": "unknown",
            "kafka_producer": "unknown",
            "redis": "unknown",
            "is_running": self.is_running
        }
        
        # Check Kafka consumer
        if self.consumer:
            try:
                # Try to get topic metadata
                topics = self.consumer.topics()
                health_status["kafka_consumer"] = "healthy"
            except Exception:
                health_status["kafka_consumer"] = "unhealthy"
                health_status["status"] = "unhealthy"
        
        # Check Kafka producer
        if self.producer:
            try:
                # Try to get metadata
                self.producer.metrics()
                health_status["kafka_producer"] = "healthy"
            except Exception:
                health_status["kafka_producer"] = "unhealthy"
                health_status["status"] = "unhealthy"
        
        # Check Redis
        if self.redis_client:
            try:
                self.redis_client.ping()
                health_status["redis"] = "healthy"
            except Exception:
                health_status["redis"] = "unhealthy"
                health_status["status"] = "unhealthy"
        
        return health_status
