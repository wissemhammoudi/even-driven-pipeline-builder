from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from source.repository.database import engine, Base  
from source.api.pipeline.router import pipeline_router
from source.config.config import auth_config, api_config
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
from source.service.keycloak_service import get_keycloak_service    
from source.service.PipelineManager.transfomrationManager.n8n_manager import N8NManager
from source.api.change_detection.router import schema_change_detection_router
from source.service.change_detection.service import ChangeDetectionService
from fastapi import Query
from typing import Optional


app = FastAPI(
    title='Data Integration Component',
    description='A RESTful API for Pipeline Manager Component',
    version=auth_config.version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        api_config.frontend_url,
        api_config.frontend_url_develop,
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
<<<<<<< Updated upstream
=======
app.include_router(cdc_router, tags=["CDC"])
app.include_router(schema_change_detection_router, tags=["Schema Change Detection"])

>>>>>>> Stashed changes
Base.metadata.create_all(bind=engine)




@app.on_event("startup")
async def startup_event():
    """Run startup tasks"""
    print("🚀 Starting application initialization...")
    
    # Try Keycloak setup first
    try:
        print("🔧 Attempting Keycloak setup...")
        keycloak_service = await get_keycloak_service()
        
        print("⏳ Waiting for Keycloak to be ready...")
        keycloak_ready = await keycloak_service.wait_for_ready(max_attempts=15, delay=3.0)
        if not keycloak_ready:
            print("❌ Keycloak is not ready after 15 attempts")
            return        
        print("✅ Keycloak is ready")
        
        print("⏳ Checking and creating Keycloak realm...")
        realm_ready = await keycloak_service.check_and_create_realm()
        if not realm_ready:
            print("❌ Failed to create Keycloak realm")
            return
        print("✅ Keycloak realm is ready")
        
        print("⏳ Setting up Keycloak...")
        setup_result = await keycloak_service.setup_keycloak()
        if not setup_result["success"]:
            print(f"❌ Keycloak setup failed: {setup_result}")
            return
        print("✅ Keycloak setup completed")
        
        print("⏳ Ensuring admin user exists...")
        admin_user_ready = await keycloak_service.ensure_admin_user_exists()
        if not admin_user_ready:
            print("❌ Failed to create admin user in Keycloak")
            return
        print("✅ Admin user created in Keycloak")
        
        print("⏳ Creating demo users...")
        await keycloak_service.create_demo_users()
        print("✅ Demo users created in Keycloak")
        
    except Exception as e:
        print(f"❌ Keycloak setup failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Initialize N8N
    try:
        print("🔧 Initializing N8N...")
        n8n_manager = N8NManager()
        n8n_manager.initialize_n8n()
        print("✅ N8N initialized successfully")
    except Exception as e:
        print(f"❌ N8N initialization failed: {str(e)}")
        import traceback
        traceback.print_exc()
    print("🎉 Application startup completed!")

@app.get("/")
def root():
    return {"message": "Event Driven Data Ingestion Service is running!"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Event Driven Data Ingestion Service",
        "version": auth_config.version,
    }

@app.get("/auth/status")
async def auth_status():
    """Check authentication service status"""
    try:
        keycloak_service = await get_keycloak_service()
        connection_test = await keycloak_service.test_connection()
        return {
            "keycloak_status": "connected" if connection_test["reachable"] else "disconnected",
            "authentication_service": "Keycloak",
            "realm": "pipeline-realm"
        }
    except Exception as e:
        return {
            "keycloak_status": "error",
            "error": str(e),
            "authentication_service": "Keycloak"
        }
