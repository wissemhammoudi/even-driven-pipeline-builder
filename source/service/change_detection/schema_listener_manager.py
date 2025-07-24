from source.service.change_detection.database_schema_detction.postgres_schema_change import PostgresSchemaChangeListener
from source.repository.pipeline.repository import PipelineRepository
from source.repository.pipeline_step.repository import StepRepository
from source.config.config import EmailConfig
from source.service.change_detection.email_notification.pipeline_email_notifier import EmailSender
from source.schema.pipeline.schema import PipelineStatusEnum

class SchemaListenerManager:
    TOOL_LISTENER_MAP = {
        "postgres": PostgresSchemaChangeListener,
    }

    def __init__(self):
        self.pipeline_schema_listeners = {}
        self.pipeline_repo = PipelineRepository()
        self.step_repo = StepRepository()
        self.email_sender = EmailSender(
            smtp_server=EmailConfig.smtp_server,
            port=EmailConfig.smtp_port,
            username=EmailConfig.smtp_username,
            password=EmailConfig.smtp_password,
            use_tls=EmailConfig.use_tls
        )

    def get_tool_from_steps(self, steps):
        if not steps:
            return None
        config = steps[0].step_config
        return config.get("schema_change_tool") 

    def extract_db_config_and_schema_from_steps(self, steps):
        print(f"[DEBUG] extract_db_config_and_schema_from_steps: steps={steps}")
        if not steps:
            return None, None
        config = steps[0].step_config
        print(f"[DEBUG] First step's step_config: {config}")
        conn_conf = config.get('connection_config', {})
        db_info = conn_conf.get('source') or conn_conf.get('extractor')
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
                print(f"[DEBUG] Extracted db_config: {db_config}, schema: {schema}")
                return db_config, schema
            except Exception as e:
                print(f"[DEBUG] Failed to extract db_config/schema from nested config: {e}")
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
            print(f"[DEBUG] Extracted db_config: {db_config}, schema: {schema}")
            return db_config, schema
        return None, None

    def start_listener(self, pipeline_id):
        print(f"[DEBUG] start_listener called for pipeline_id={pipeline_id}")
        if pipeline_id in self.pipeline_schema_listeners:
            return
        steps = self.step_repo.get_step_by_pipeline(pipeline_id)
        print(f"[DEBUG] Steps fetched for pipeline_id={pipeline_id}: {steps}")
        db_config, schema = self.extract_db_config_and_schema_from_steps(steps)
        tool = self.get_tool_from_steps(steps)
        ListenerClass = self.TOOL_LISTENER_MAP.get(tool)
        if not ListenerClass:
            print(f"[ERROR] No schema change listener implemented for tool: {tool}")
            return
        if db_config and schema:
            tables_to_monitor = self.extract_tables_to_monitor_from_steps(steps)
            print(f"[DEBUG] Starting {tool} SchemaChangeListener with db_config={db_config}, schema={schema}, tables={tables_to_monitor}")
            listener = ListenerClass(
                db_config, schema, pipeline_id=pipeline_id,
                email_sender=self.email_sender, tables_to_monitor=tables_to_monitor
            )
            listener.start()
            self.pipeline_schema_listeners[pipeline_id] = listener

    def stop_listener(self, pipeline_id):
        listener = self.pipeline_schema_listeners.pop(pipeline_id, None)
        if listener:
            listener.stop()

    def extract_tables_to_monitor_from_steps(self, steps):
        if not steps:
            return []
        tables = []
        for step in steps:
            step_config = step.step_config
            if 'table_sync_config' in step_config:
                tables.extend(step_config['table_sync_config'])
            elif 'tables' in step_config:
                tables.extend(step_config['tables'])
        return list(set(tables))

    def restore_all_listeners(self):
        pipeline_ids = self.pipeline_repo.get_all_pipelines_ids()
        for pipeline_id in pipeline_ids:
            pipeline = self.pipeline_repo.get_Active_Pipeline_by_id(pipeline_id)
            if not pipeline or pipeline.is_deleted or pipeline.status == PipelineStatusEnum.broken:
                continue
            steps = self.step_repo.get_step_by_pipeline(pipeline_id)
            db_config, schema = self.extract_db_config_and_schema_from_steps(steps)
            tool = self.get_tool_from_steps(steps)
            ListenerClass = self.TOOL_LISTENER_MAP.get(tool)
            if not ListenerClass:
                print(f"[ERROR] No schema change listener implemented for tool: {tool}")
                continue
            if db_config and schema:
                if pipeline_id not in self.pipeline_schema_listeners:
                    tables_to_monitor = self.extract_tables_to_monitor_from_steps(steps)
                    listener = ListenerClass(db_config, schema, pipeline_id=pipeline_id, email_sender=self.email_sender, tables_to_monitor=tables_to_monitor)
                    listener.start()
                    self.pipeline_schema_listeners[pipeline_id] = listener 