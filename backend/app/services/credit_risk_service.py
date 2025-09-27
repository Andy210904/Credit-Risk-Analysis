from app.models.credit_risk import CreditRiskRequest, RiskLevel
from typing import Dict, List
import numpy as np
import logging

logger = logging.getLogger(__name__)

class CreditRiskService:
    def __init__(self):
        # Initialize any ML models or external services here
        pass
    
    async def calculate_risk_score(self, request: CreditRiskRequest) -> Dict:
        """
        Calculate credit risk score based on financial data
        """
        try:
            # Simple risk scoring algorithm (replace with actual ML model)
            score = 0
            
            # Credit score factor (30% weight)
            if request.credit_score >= 750:
                score += 30
            elif request.credit_score >= 650:
                score += 20
            elif request.credit_score >= 550:
                score += 10
            else:
                score += 0
                
            # Income to loan ratio (25% weight)
            income_ratio = request.loan_amount / request.income if request.income > 0 else 10
            if income_ratio <= 2:
                score += 25
            elif income_ratio <= 4:
                score += 15
            elif income_ratio <= 6:
                score += 5
            else:
                score += 0
                
            # Debt to income ratio (25% weight)
            if request.debt_to_income_ratio <= 0.3:
                score += 25
            elif request.debt_to_income_ratio <= 0.4:
                score += 15
            elif request.debt_to_income_ratio <= 0.5:
                score += 5
            else:
                score += 0
                
            # Employment length (20% weight)
            if request.employment_length >= 5:
                score += 20
            elif request.employment_length >= 2:
                score += 15
            elif request.employment_length >= 1:
                score += 10
            else:
                score += 5
                
            # Determine risk level
            if score >= 70:
                risk_level = RiskLevel.LOW
                explanation = "Low risk: Strong financial profile with good credit score and stable employment."
            elif score >= 50:
                risk_level = RiskLevel.MEDIUM
                explanation = "Medium risk: Acceptable financial profile but some areas of concern."
            else:
                risk_level = RiskLevel.HIGH
                explanation = "High risk: Weak financial profile with multiple risk factors."
                
            recommendations = self._generate_recommendations(request, risk_level)
            
            return {
                "risk_level": risk_level,
                "risk_score": score,
                "explanation": explanation,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {str(e)}")
            raise
    
    def _generate_recommendations(self, request: CreditRiskRequest, risk_level: RiskLevel) -> List[str]:
        """
        Generate personalized recommendations based on risk assessment
        """
        recommendations = []
        
        if request.credit_score < 650:
            recommendations.append("Improve credit score by paying bills on time and reducing credit utilization")
            
        if request.debt_to_income_ratio > 0.4:
            recommendations.append("Reduce debt-to-income ratio by paying down existing debts")
            
        if request.employment_length < 2:
            recommendations.append("Build employment history for better loan terms")
            
        if risk_level == RiskLevel.HIGH:
            recommendations.append("Consider a co-signer or collateral to improve loan approval chances")
            
        return recommendations
    
    async def get_statistics(self) -> Dict:
        """
        Get mock statistics (replace with actual database queries)
        """
        return {
            "total_analyses": 156,
            "high_risk_count": 23,
            "medium_risk_count": 67,
            "low_risk_count": 66
        }
    
    async def get_analysis_history(self) -> List[Dict]:
        """
        Get mock analysis history (replace with actual database queries)
        """
        return [
            {
                "id": 1,
                "risk_level": "low",
                "risk_score": 75,
                "created_at": "2023-12-01T10:00:00"
            },
            {
                "id": 2,
                "risk_level": "medium", 
                "risk_score": 55,
                "created_at": "2023-12-01T11:00:00"
            }
        ]