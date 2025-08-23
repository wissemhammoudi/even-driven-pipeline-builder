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

from source.service.PipelineManager.transfomrationManager.n8n_manager import N8NManager


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
Base.metadata.create_all(bind=engine)




@app.on_event("startup")
async def startup_event():
    """Run startup tasks"""
    print("Starting up Event-Driven Pipeline Builder...")
    
    try:
        from source.service.keycloak_service import get_keycloak_service
        
        print("🔐 Setting up Keycloak authentication...")
        
        keycloak_service = get_keycloak_service()
        
        print("🔐 Waiting for Keycloak to be ready...")
        keycloak_ready = await keycloak_service.wait_for_ready(max_attempts=15, delay=3.0)
        if not keycloak_ready:
            print("❌ Keycloak failed to become ready")
            return
        
        print("✅ Keycloak is ready")
        
        realm_ready = await keycloak_service.check_and_create_realm()
        if not realm_ready:
            print("❌ Failed to ensure realm is ready")
            return
        
        print("✅ Keycloak realm is ready")
        
        setup_result = await keycloak_service.setup_keycloak()
        if not setup_result["success"]:
            print(f"❌ Keycloak setup failed: {setup_result['message']}")
            return
        
        print("✅ Keycloak setup completed successfully")
        
        print("👤 Ensuring admin user exists...")
        admin_user_ready = await keycloak_service.ensure_admin_user_exists()
        if not admin_user_ready:
            print("❌ Failed to ensure admin user exists")
            return
        
        print("✅ Admin user is ready")
        
        print("👥 Creating demo users...")
        demo_users_created = await keycloak_service.create_demo_users()
        if demo_users_created:
            print("✅ Demo users created successfully")
        else:
            print("⚠️ Demo users creation failed or skipped")
        
    except Exception as e:
        print(f"❌ Keycloak setup failed: {e}")
        return
    
    try:
        print("🔧 Setting up N8N...")
        n8n_manager = N8NManager()
        n8n_manager.initialize_n8n()
        print("✅ N8N setup completed")
    except Exception as e:
        print(f"❌ N8N initialization failed: {e}")
    
    try:
        print("👥 Initial users are managed by Keycloak")
    except Exception as e:
        print(f"❌ User initialization failed: {e}")
    
    print("🎉 Startup completed successfully!")

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
        "authentication": "Keycloak-based"
    }

@app.get("/auth/status")
async def auth_status():
    """Check authentication service status"""
    try:
        from source.service.keycloak_service import get_keycloak_service
        keycloak_service = get_keycloak_service()
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
