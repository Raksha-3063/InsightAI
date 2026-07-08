from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.app.config import settings
from backend.app.database.connection import connect_to_mongo, close_mongo_connection
from backend.app.auth.routes import router as auth_router
from backend.app.routes.project import router as project_router
from backend.app.routes.dataset import router as dataset_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    await connect_to_mongo()
    yield
    # Shutdown: Close connection
    await close_mongo_connection()

app = FastAPI(
    title="InsightAI API",
    description="AI-Powered Business Intelligence & Data Analytics Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(project_router, prefix="/api/projects", tags=["Projects"])
app.include_router(dataset_router, prefix="/api/projects", tags=["Datasets"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
