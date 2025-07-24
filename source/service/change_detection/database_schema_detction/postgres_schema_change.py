import psycopg2
import select
import threading
import time
import logging
import json
from source.service.change_detection.email_notification.pipeline_email_notifier import PipelineEmailNotifier
from source.repository.pipeline.repository import PipelineRepository
from source.repository.change_detection.repository import SchemaChangeRepository
from source.schema.change_detection.schema import SchemaChangeTypeEnum
from source.service.change_detection.sql_to_humainLanguage.message_generator import SchemaChangeMessageGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PostgresSchemaChangeListener:
    def __init__(self, db_config: dict, schema: str, pipeline_id=None, email_sender=None, channel='schema_changes', tables_to_monitor=None):
        self.db_config = db_config
        self.schema = schema
        self.channel = ''.join(filter(str.isalnum, channel))
        self.pipeline_id = pipeline_id
        self.email_sender = email_sender
        self._stop_event = threading.Event()
        self._thread = None
        self.conn = None
        self.cur = None
        self.pipeline_repo = PipelineRepository()
        self.schema_change_repo = SchemaChangeRepository()
        self.tables_to_monitor = tables_to_monitor or []

    def start(self):
        if self._thread and self._thread.is_alive():
            logging.info('SchemaChangeListener is already running.')
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._setup_and_listen, daemon=True)
        self._thread.start()
        logging.info('SchemaChangeListener started.')

    def stop(self):
        """Stops the listener thread and closes database connections."""
        logging.info('Stopping SchemaChangeListener...')
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        logging.info('SchemaChangeListener stopped.')

    def _setup_and_listen(self):
        while not self._stop_event.is_set():
            try:
                self.conn = psycopg2.connect(**self.db_config)
                self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
                self.cur = self.conn.cursor()

                logging.info("Setting up database event trigger...")
                self._setup_event_trigger()

                self.cur.execute(f"LISTEN {self.channel};")
                logging.info(f"Successfully connected and listening to channel: {self.channel}")

                while not self._stop_event.is_set():
                    if select.select([self.conn], [], [], 5) == ([], [], []):
                        continue

                    self.conn.poll()
                    while self.conn.notifies:
                        notify = self.conn.notifies.pop(0)
                        logging.info(f"Received NOTIFY on '{notify.channel}'")
                        self.on_schema_change(notify.payload)

            except (psycopg2.InterfaceError, psycopg2.OperationalError) as e:
                logging.error(f"Connection error: {e}. Reconnecting in 5 seconds...")
                if self.cur: self.cur.close()
                if self.conn: self.conn.close()
                self.cur, self.conn = None, None
                time.sleep(5)
            except Exception as e:
                logging.error(f"An unexpected error occurred in listener loop: {e}. Retrying in 5 seconds...")
                time.sleep(5)
            finally:
                if self.cur: self.cur.close()
                if self.conn: self.conn.close()
                self.cur, self.conn = None, None

    def _setup_event_trigger(self):
        """
        Creates or replaces the database function and event trigger required
        to capture DDL changes and send them as a JSON payload.
        """
        safe_schema_name = ''.join(filter(str.isalnum, self.schema))
        func_name = f'notify_ddl_change_{safe_schema_name}'
        trigger_name = f'ddl_notify_trigger_{safe_schema_name}'
        
        tables_filter = ""
        if self.tables_to_monitor:
            table_identities = [f"{self.schema}.{t}" for t in self.tables_to_monitor]
            table_list = "', '".join(table_identities)
            tables_filter = f"AND obj.object_identity IN ('{table_list}')"
        else:
            tables_filter = f"AND obj.schema_name = '{self.schema}'"
        
        function_sql = f'''
        CREATE OR REPLACE FUNCTION {func_name}() RETURNS event_trigger AS $$
        DECLARE
            obj record;
            payload json;
        BEGIN
            FOR obj IN SELECT * FROM pg_event_trigger_ddl_commands() LOOP
                IF TRUE {tables_filter} THEN
                    payload = json_build_object(
                        'command_tag', obj.command_tag,
                        'schema_name', obj.schema_name,
                        'object_type', obj.object_type,
                        'object_identity', obj.object_identity,
                        'in_extension', obj.in_extension,
                        'command', current_query()
                    );
                    PERFORM pg_notify('{self.channel}', payload::text);
                END IF;
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
        '''
        self.cur.execute(function_sql)
        trigger_sql = f'''
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_event_trigger WHERE evtname = '{trigger_name}'
            ) THEN
                EXECUTE 'CREATE EVENT TRIGGER {trigger_name}
                         ON ddl_command_end
                         WHEN TAG IN (''ALTER TABLE'', ''CREATE TABLE'', ''DROP TABLE'')
                         EXECUTE FUNCTION {func_name}();';
            END IF;
        END$$;
        '''
        self.cur.execute(trigger_sql)
        logging.info(f"Event trigger '{trigger_name}' and function '{func_name}' are configured.")
        if self.tables_to_monitor:
            logging.info(f"Monitoring specific tables: {', '.join(self.tables_to_monitor)}")
        else:
            logging.info(f"Monitoring all tables in schema '{self.schema}'")


    def on_schema_change(self, payload_str: str):
        logging.info(f"Processing schema change payload: {payload_str}")
        try:
            change_data = json.loads(payload_str)
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON payload: {payload_str}")
            return

        if not self.pipeline_id:
            logging.warning("No pipeline_id configured, skipping further actions.")
            return

        pipeline_name = "N/A"
        try:
            pipeline = self.pipeline_repo.get_pipline_by_id(self.pipeline_id)
            if pipeline:
                pipeline_name = getattr(pipeline, 'name', 'N/A')
        except Exception as e:
            logging.error(f"Could not retrieve pipeline details for ID {self.pipeline_id}: {e}")

        is_breaking = self.is_breaking_change(change_data)
        
        # Generate human-readable message
        human_readable_message = SchemaChangeMessageGenerator.generate_human_readable_message(change_data)
        
        # Add human-readable message to the change data
        enhanced_change_data = change_data.copy()
        enhanced_change_data['human_readable_message'] = human_readable_message
        enhanced_change_data['is_breaking'] = is_breaking
        
        try:
            change_type = SchemaChangeTypeEnum.breaking if is_breaking else SchemaChangeTypeEnum.non_breaking
            payload_json = json.dumps(enhanced_change_data)
            self.schema_change_repo.add_event(
                pipeline_id=self.pipeline_id,
                change_type=change_type,
                payload=payload_json
            )
            logging.info(f"Schema change event logged to database for pipeline {self.pipeline_id}")
        except Exception as e:
            logging.error(f"Failed to log schema change event to database: {e}")
        
        if self.email_sender:
            try:
                notifier = PipelineEmailNotifier(
                    pipeline_id=self.pipeline_id,
                    email_sender=self.email_sender,
                    pipeline_name=pipeline_name,
                    human_readable_message=human_readable_message,
                    technical_details=json.dumps(change_data, indent=2)
                )
                logging.info(f"Sending schema change notification for pipeline {self.pipeline_id}")
                notifier.send_schema_change_notification()
            except Exception as e:
                logging.error(f"Failed to send email notification: {e}")

        if is_breaking:
            logging.warning(f"Breaking change detected for pipeline {self.pipeline_id}. Marking as deprecated.")
            self.mark_pipeline_as_broken()

    def is_breaking_change(self, change_data: dict) -> bool:
        command_tag = change_data.get('command_tag', '').upper()
        full_command = change_data.get('command', '').upper()
        if command_tag in ('ALTER TABLE', 'DROP TABLE'):
            if 'RENAME COLUMN' in full_command:
                return True
            if 'ALTER COLUMN' in full_command and 'TYPE' in full_command:
                return True
            if 'RENAME TO' in full_command:
                return True
        return False

    def mark_pipeline_as_broken(self):
        if not self.pipeline_id:
            return
        try:
            result = self.pipeline_repo.mark_pipeline_broken(self.pipeline_id)
            if result:
                logging.info(f"Pipeline {self.pipeline_id} successfully marked as broken.")
            else:
                logging.warning(f"Could not find pipeline with ID {self.pipeline_id} to mark as broken.")
        except Exception as e:
            logging.error(f"Failed to mark pipeline {self.pipeline_id} as broken: {e}")