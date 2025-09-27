from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CreditRiskRequest(BaseModel):
    income: float
    credit_score: int
    loan_amount: float
    employment_length: float
    debt_to_income_ratio: float

class CreditRiskResponse(BaseModel):
    risk_level: RiskLevel
    risk_score: float
    explanation: str
    recommendations: Optional[list] = []
    timestamp: datetime

class CreditRiskAnalysis(BaseModel):
    id: Optional[int] = None
    income: float
    credit_score: int
    loan_amount: float
    employment_length: float
    debt_to_income_ratio: float
    risk_level: RiskLevel
    risk_score: float
    explanation: str
    created_at: Optional[datetime] = None

class Statistics(BaseModel):
    total_analyses: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int