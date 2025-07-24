from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from source.repository.database import engine, Base  
from source.api.pipeline.router import pipeline_router
from source.config.config import AuthConfig,APIConfig
from source.api.user.router import user_router
from source.api.pipeline_step.router import step_router
from source.api.step_config.router import step_config_router
from source.api.step_configuration_association.router import configuration_router
from source.api.pipeline_run.router import pipeline_run_router
from source.api.superset.router import superset_router
from source.api.agentic_transformation.router import router_transformation
from source.api.user_pipeline_access.router import user_pipeline_access_router
from source.api.dashboard.router import dashboard_router
from source.api.pipeline_dashboard.router import pipeline_dashboard_router
from source.api.change_detection.router import schema_change_detection_router
from source.service.change_detection.schema_listener_manager import SchemaListenerManager
app = FastAPI(
    title='Data Integration Component',
    description='A RESTful API for Pipeline Manager Component',
    version=AuthConfig.version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        APIConfig.frontend_url,
        APIConfig.frontend_url_develop,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pipeline_router,tags=["Pipelines"])
app.include_router(user_router,tags=["User"])
app.include_router(step_router,tags=["Pipelines Steps"])
app.include_router(step_config_router,tags=["step Configuration"])
app.include_router(configuration_router, tags=["step Configuration associations"])
app.include_router(pipeline_run_router, tags=["Pipeline Runs"])
app.include_router(superset_router, tags=["superset"])
app.include_router(router_transformation, tags=["transformation"])
app.include_router(user_pipeline_access_router, tags=["User Pipeline Access"])
app.include_router(dashboard_router, tags=["Dashboard"])
app.include_router(pipeline_dashboard_router, tags=["Pipeline Dashboard"])
app.include_router(schema_change_detection_router, tags=["Schema Change Detection"])
Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def on_startup():
    manager = SchemaListenerManager()
    manager.restore_all_listeners()


@app.get("/")
def root():
    return {"message": "Event Driven Data Ingestion Service is running!"}
