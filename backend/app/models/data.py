from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class RiskBucket(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Sector(str, Enum):
    TECHNOLOGY = "Technology"
    MATERIALS = "Materials"
    CONSUMER_GOODS = "Consumer Goods"
    TELECOMMUNICATIONS = "Telecommunications"
    REAL_ESTATE = "Real Estate"
    MANUFACTURING = "Manufacturing"
    ENERGY = "Energy"
    CHEMICALS = "Chemicals"
    PHARMACEUTICALS = "Pharmaceuticals"
    RETAIL = "Retail"
    INDUSTRIALS = "Industrials"
    MEDIA = "Media"
    AUTOMOTIVE = "Automotive"
    HEALTHCARE = "Healthcare"
    TRANSPORTATION = "Transportation"
    UTILITIES = "Utilities"

class OwnershipType(str, Enum):
    PRIVATE = "Private"
    PUBLIC = "Public"
    STATE = "State"

class AuditorTier(str, Enum):
    BIG4 = "Big4"
    OTHER = "Other"

class IndustryCyclicality(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class HedgingPolicy(str, Enum):
    NONE = "None"
    PARTIAL = "Partial"
    COMPREHENSIVE = "Comprehensive"

class CovenantQuality(str, Enum):
    WEAK = "Weak"
    STANDARD = "Standard"
    STRONG = "Strong"

class SanctionsExposure(str, Enum):
    NONE = "None"
    INDIRECT = "Indirect"
    DIRECT = "Direct"

class CreditEntity(BaseModel):
    entity_id: str
    entity_name: str
    sector: Sector
    country: str
    revenue_usd_m: float
    ebitda_margin_pct: float
    ebit_margin_pct: float
    cash_usd_m: float
    total_assets_usd_m: float
    equity_usd_m: float
    net_debt_usd_m: float
    debt_to_equity: float
    interest_expense_usd_m: float
    interest_coverage: float
    operating_cf_usd_m: float
    capex_usd_m: float
    fcf_usd_m: float
    dscr: float
    current_ratio: float
    quick_ratio: float
    dso_days: int
    dpo_days: int
    dio_days: int
    revenue_cagr_3y_pct: float
    years_in_operation: int
    ownership_type: OwnershipType
    auditor_tier: AuditorTier
    governance_score_0_100: int
    esg_controversies_3y: int
    country_risk_0_100: int
    industry_cyclicality: IndustryCyclicality
    fx_revenue_pct: int
    hedging_policy: HedgingPolicy
    collateral_coverage_pct: int
    covenant_quality: CovenantQuality
    payment_incidents_12m: int
    legal_disputes_open: int
    sanctions_exposure: Optional[SanctionsExposure]
    financials_audited: bool
    pd_1y_pct: float
    lgd_pct: float
    ead_usd_m: float
    risk_bucket: RiskBucket
    implied_rating: str

class CreditEntitiesList(BaseModel):
    total_count: int
    entities: List[CreditEntity]

class FinancialSummary(BaseModel):
    total_entities: int
    avg_revenue_usd_m: float
    avg_ebitda_margin_pct: float
    avg_pd_1y_pct: float
    risk_distribution: dict
    sector_distribution: dict
    country_distribution: dict