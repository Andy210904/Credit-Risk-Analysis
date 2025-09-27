from fastapi import APIRouter, HTTPException
from app.models.ml_service import MLRequest, MLResponse
from app.services.ml_service import MLService
import logging

router = APIRouter()
ml_service = MLService()

logger = logging.getLogger(__name__)

@router.post("/analyze", response_model=MLResponse)
async def analyze_with_llm(request: MLRequest):
    """
    Analyze data using LLM service
    """
    try:
        response = await ml_service.process_llm_request(request.prompt, request.context)
        return MLResponse(
            response=response["response"],
            confidence=response.get("confidence"),
            metadata=response.get("metadata", {})
        )
    except Exception as e:
        logger.error(f"Error processing LLM request: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process LLM request")

@router.post("/credit-analysis")
async def credit_analysis_with_llm(request: MLRequest):
    """
    Perform credit analysis using LLM
    """
    try:
        # Create a specialized prompt for credit analysis
        credit_prompt = f"""
        Analyze the following credit information and provide insights:
        {request.prompt}
        
        Please provide:
        1. Risk assessment
        2. Key factors affecting the credit decision
        3. Recommendations
        """
        
        response = await ml_service.process_llm_request(credit_prompt, request.context)
        return {"analysis": response}
    except Exception as e:
        logger.error(f"Error processing credit analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process credit analysis")