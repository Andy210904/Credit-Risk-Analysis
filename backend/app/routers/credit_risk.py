from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.credit_risk import CreditRiskRequest, CreditRiskResponse, Statistics, RiskLevel
from app.services.credit_risk_service import CreditRiskService
from datetime import datetime
import logging

router = APIRouter()
credit_service = CreditRiskService()

logger = logging.getLogger(__name__)

@router.post("/analyze", response_model=CreditRiskResponse)
async def analyze_credit_risk(request: CreditRiskRequest):
    """
    Analyze credit risk based on provided financial data
    """
    try:
        # Calculate risk score using the service
        risk_data = await credit_service.calculate_risk_score(request)
        
        return CreditRiskResponse(
            risk_level=risk_data["risk_level"],
            risk_score=risk_data["risk_score"],
            explanation=risk_data["explanation"],
            recommendations=risk_data.get("recommendations", []),
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error analyzing credit risk: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze credit risk")

@router.get("/statistics", response_model=Statistics)
async def get_statistics():
    """
    Get credit risk analysis statistics
    """
    try:
        stats = await credit_service.get_statistics()
        return Statistics(**stats)
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

@router.get("/history")
async def get_analysis_history():
    """
    Get history of credit risk analyses
    """
    try:
        history = await credit_service.get_analysis_history()
        return {"history": history}
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch analysis history")