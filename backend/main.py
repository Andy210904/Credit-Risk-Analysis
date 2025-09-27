from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import credit_risk, ml_service
from app.config import settings
import uvicorn

app = FastAPI(
    title="Credit Risk Analysis API",
    description="Backend API for Credit Risk Analysis Application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(credit_risk.router, prefix="/api/credit-risk", tags=["credit-risk"])
app.include_router(ml_service.router, prefix="/api/ml", tags=["ml-service"])

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