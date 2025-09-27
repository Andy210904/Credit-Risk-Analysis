from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import data, ml_service, frontend
from app.config import settings
from app.services.database_service import database_service
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Credit Risk Analysis API",
    description="Backend API for Credit Risk Analysis Application",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        # Initialize database - this will create tables if they don't exist
        database_service.ensure_database_exists()
        logger.info("Database initialized successfully on startup")
    except Exception as e:
        logger.error(f"Failed to initialize database on startup: {e}")
        # Don't raise - let the app start anyway

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(ml_service.router, prefix="/api/ml", tags=["ml-service"])
app.include_router(frontend.router, prefix="/api/frontend", tags=["frontend"])

@app.get("/")
async def root():
    return {"message": "Credit Risk Analysis API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )