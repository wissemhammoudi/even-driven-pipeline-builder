import psycopg2
import select
import threading
import time
import logging
import re
import json

class PostgresPipelineSchemaChangeListener:
    """Listens for schema changes in PostgreSQL databases and reports them to an event queue."""
    def __init__(self, pipeline_configs, event_queue, event_queue_lock=None):
        self.pipeline_configs = pipeline_configs
        self.event_queue = event_queue
        self.event_queue_lock = event_queue_lock
        self._stop_event = threading.Event()
        self._thread = None
        self.connections = []  
    
    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._setup_and_listen, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        for conn, cur, _, _ in self.connections:
            if cur:
                cur.close()
            if conn:
                conn.close()
        self.connections = []

    def _setup_and_listen(self):
        for config in self.pipeline_configs:
            db_config = config['db_config']       
            schema = config['schema']             
            pipeline_id = config['pipeline_id']    
            tables_to_monitor = config.get('tables_to_monitor', [])     
            
            schema_channel = f"schema_changes_{pipeline_id}"
            
            try:
                conn = psycopg2.connect(**db_config)
                conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
                cur = conn.cursor()
                
                self._setup_event_trigger(cur, schema, schema_channel, tables_to_monitor)
                cur.execute(f"LISTEN {schema_channel};")                
                self.connections.append((conn, cur, pipeline_id, schema_channel))
            except Exception as e:
                logging.error(f"Failed to connect/listen for pipeline {pipeline_id}: {e}")
        
        while not self._stop_event.is_set():
            for conn, cur, pipeline_id, schema_channel in self.connections:
                try:
                    if select.select([conn], [], [], 1) == ([], [], []):
                        continue
                    conn.poll()
                    while conn.notifies:
                        notify = conn.notifies.pop(0)
                        
                        event_data = {
                            'pipeline_id': pipeline_id, 
                            'payload': notify.payload,
                            'change_type': 'schema'
                        }
                        self.event_queue.put(event_data)
                        print(f"Schema change event detected: {event_data}")
                            
                except Exception as e:
                    logging.error(f"Error polling/listening for pipeline {pipeline_id}: {e}")
            time.sleep(0.1)

    def _setup_event_trigger(self, cur, schema, channel, tables_to_monitor):
        safe_schema_name = re.sub(r'\W+', '', schema)
        func_name = f'notify_ddl_change_{safe_schema_name}_{channel}'
        trigger_name = f'ddl_notify_trigger_{safe_schema_name}_{channel}'        
        tables_filter = ""
        if tables_to_monitor:
            conditions = []
            for t in tables_to_monitor:
                table_identity = f"{schema}.{t}"
                conditions.append(f"(obj.object_identity = '{table_identity}' OR obj.object_identity LIKE '{table_identity}.%')")
            tables_filter = "AND (" + " OR ".join(conditions) + ")"
        else:
            tables_filter = f"AND obj.schema_name = '{schema}'"
        
        function_sql = f'''
        CREATE OR REPLACE FUNCTION {func_name}() RETURNS event_trigger AS $$
        DECLARE
            obj record;
            payload json;
            change_details json;
            is_breaking boolean := false;
        BEGIN
            FOR obj IN SELECT * FROM pg_event_trigger_ddl_commands() LOOP
                IF TRUE {tables_filter} THEN
                    is_breaking := CASE 
                        WHEN obj.command_tag = 'ALTER TABLE' AND current_query() LIKE '%RENAME COLUMN%' THEN true
                        WHEN obj.command_tag = 'ALTER TABLE' AND current_query() LIKE '%RENAME TO%' THEN true
                        WHEN obj.command_tag = 'ALTER TABLE' AND current_query() LIKE '%ALTER COLUMN%TYPE%' THEN true
                        ELSE false
                    END;
                    
                    change_details := json_build_object(
                        'command_tag', obj.command_tag,
                        'schema_name', obj.schema_name,
                        'object_type', obj.object_type,
                        'object_identity', obj.object_identity,
                        'command', current_query(),
                        'is_breaking', is_breaking,
                        'timestamp', now(),
                        'transaction_id', txid_current(),
                        'change_category', CASE 
                            WHEN obj.command_tag = 'CREATE TABLE' THEN 'table_creation'
                            WHEN obj.command_tag = 'ALTER TABLE' AND current_query() LIKE '%ADD COLUMN%' THEN 'column_addition'
                            WHEN obj.command_tag = 'ALTER TABLE' AND current_query() LIKE '%DROP COLUMN%' THEN 'column_removal'
                            WHEN obj.command_tag = 'ALTER TABLE' AND current_query() LIKE '%RENAME COLUMN%' THEN 'column_rename'
                            WHEN obj.command_tag = 'ALTER TABLE' AND current_query() LIKE '%RENAME TO%' THEN 'table_rename'
                            WHEN obj.command_tag = 'ALTER TABLE' AND current_query() LIKE '%ALTER COLUMN%TYPE%' THEN 'column_type_change'
                            WHEN obj.command_tag = 'ALTER TABLE' AND current_query() LIKE '%ADD CONSTRAINT%' THEN 'constraint_addition'
                            WHEN obj.command_tag = 'ALTER TABLE' AND current_query() LIKE '%DROP CONSTRAINT%' THEN 'constraint_removal'
                            WHEN obj.command_tag = 'DROP TABLE' THEN 'table_removal'
                            ELSE 'other'
                        END
                    );
                    
                    PERFORM pg_notify('{channel}', change_details::text);
                END IF;
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
        '''
        cur.execute(function_sql)
        
        trigger_sql = f'''
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_event_trigger WHERE evtname = '{trigger_name}'
            ) THEN
                EXECUTE 'CREATE EVENT TRIGGER {trigger_name}
                        ON ddl_command_end
                        WHEN TAG IN (''ALTER TABLE'', ''CREATE TABLE'', ''DROP TABLE'', ''CREATE INDEX'', ''DROP INDEX'')
                        EXECUTE FUNCTION {func_name}();';
            END IF;
        END$$;
        '''
        cur.execute(trigger_sql)


class PostgresPipelineDataTracker:
    """Tracks data changes in PostgreSQL databases and reports them to an event queue."""
    def __init__(self, pipeline_configs, event_queue, event_queue_lock=None):
        self.pipeline_configs = pipeline_configs
        self.event_queue = event_queue
        self.event_queue_lock = event_queue_lock
        self._stop_event = threading.Event()
        self._thread = None
        self.connections = []
        
    def start(self):
        """Start tracking data changes for all configured pipelines"""
        if self._thread and self._thread.is_alive():
            return
            
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._setup_and_track, daemon=True)
        self._thread.start()
        
    def stop(self):
        """Stop tracking data changes"""
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join(timeout=5)
            
        # Close all connections
        for conn in self.connections:
            try:
                conn.close()
            except Exception as e:
                print(f"Error closing connection: {e}")
                
        self.connections = []
        
    def _setup_and_track(self):
        """Setup connections and track data changes"""
        # Implementation would track data changes using triggers or other mechanisms
        pass
        
    def mark_changes_as_synced(self, pipeline_id: int, table_name: str = None):
        """Mark data changes as synced for a specific pipeline and optionally a specific table"""
        # Implementation would mark changes as synced in the tracking system
        return True
