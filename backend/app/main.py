import time
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database.connection import db_helper, connect_to_mongo, close_mongo_connection
from app.auth.routes import router as auth_router
from app.routes.project import router as project_router
from app.routes.dataset import router as dataset_router
from app.routes.model import router as model_router
from app.routes.forecast import router as forecast_router
from app.routes.copilot import router as copilot_router
from app.routes.job import router as job_router

# Monitoring & Security Middleware
from app.monitoring.logging import setup_structured_logging
from app.monitoring.metrics import expose_prometheus_metrics, REQUEST_COUNT, REQUEST_LATENCY
from app.middleware.rate_limit import RateLimitMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    await connect_to_mongo()
    setup_structured_logging()
    yield
    # Shutdown: Close connection
    await close_mongo_connection()

app = FastAPI(
    title="InsightAI API",
    description="AI-Powered Business Intelligence & Data Analytics Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Setup CORS & rate limiting middleware
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics interceptor middleware
@app.middleware("http")
async def add_metrics_middleware(request, call_next):
    start_time = time.time()
    path = request.url.path
    method = request.method
    
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        raise e
    finally:
        duration = time.time() - start_time
        if not path.startswith("/metrics") and not path.startswith("/health"):
            REQUEST_COUNT.labels(method=method, endpoint=path, status=status_code).inc()
            REQUEST_LATENCY.labels(method=method, endpoint=path).observe(duration)
            
    return response

# Register routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(project_router, prefix="/api/projects", tags=["Projects"])
app.include_router(dataset_router, prefix="/api/projects", tags=["Datasets"])
app.include_router(model_router, prefix="/api/projects", tags=["Models"])
app.include_router(forecast_router, prefix="/api/projects", tags=["Forecasting"])
app.include_router(copilot_router, prefix="/api/projects", tags=["AI Copilot"])
app.include_router(job_router, prefix="/api/projects", tags=["Background Jobs"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/ready")
async def readiness_check():
    try:
        # Ping DB
        await db_helper.db.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
        raise HTTPException(status_code=503, detail="Database is unreachable.")
        
    return {
        "status": "ready",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/metrics")
def get_metrics():
    return expose_prometheus_metrics()
