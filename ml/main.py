from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import os
from src.llm_service import LLMService
from src.credit_analyzer import CreditAnalyzer

app = FastAPI(
    title="Credit Risk ML Service",
    description="Machine Learning service for Credit Risk Analysis with LLM integration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
llm_service = LLMService()
credit_analyzer = CreditAnalyzer()

class PromptRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = {}
    model: Optional[str] = "gpt-3.5-turbo"

class AnalysisRequest(BaseModel):
    data: Dict[str, Any]
    analysis_type: str = "credit_risk"

@app.get("/")
async def root():
    return {"message": "Credit Risk ML Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ml-service"}

@app.post("/analyze")
async def analyze_with_llm(request: PromptRequest):
    """
    Analyze data using LLM with the provided prompt
    """
    try:
        result = await llm_service.process_prompt(
            prompt=request.prompt,
            context=request.context,
            model=request.model
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/credit-analysis")
async def credit_risk_analysis(request: AnalysisRequest):
    """
    Specialized credit risk analysis using ML models and LLM
    """
    try:
        result = await credit_analyzer.analyze_credit_risk(request.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Credit analysis failed: {str(e)}")

@app.post("/explain-decision")
async def explain_credit_decision(request: AnalysisRequest):
    """
    Explain credit risk decision using LLM
    """
    try:
        explanation = await credit_analyzer.explain_decision(request.data)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decision explanation failed: {str(e)}")

@app.get("/models/status")
async def get_model_status():
    """
    Get status of available models and services
    """
    return {
        "llm_service": llm_service.get_status(),
        "credit_analyzer": credit_analyzer.get_status(),
        "available_models": llm_service.get_available_models()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )