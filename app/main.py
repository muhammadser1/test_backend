from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import config
from app.db import connect_to_mongo, close_mongo_connection
from app.api.v1.api import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events - startup and shutdown
    """
    # Startup
    logger.info("🚀 Starting General Institute System API...")
    try:
        connect_to_mongo()
        logger.info("✅ Application startup complete")
    except Exception as e:
        logger.error(f"❌ Failed to start application: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down General Institute System API...")
    close_mongo_connection()
    logger.info("✅ Application shutdown complete")


app = FastAPI(
    title="General Institute System",
    description="A comprehensive backend system for managing institute operations",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins= allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """
    Root endpoint - Hello World
    """
    return {
        "message": "Hello World",
        "app": "General Institute System",
        "version": "1.0.0"
    }

