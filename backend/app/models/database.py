from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class ClientData(Base):
    __tablename__ = "client_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Core identification
    entity_id = Column(String(50), index=True)
    entity_name = Column(String(200))
    
    # Financial metrics - essential fields from frontend
    debt_to_equity = Column(Float)
    dscr = Column(Float)  # Debt Service Coverage Ratio
    current_ratio = Column(Float)
    ebitda_margin_pct = Column(Float)
    revenue_usd_m = Column(Float)
    years_in_operation = Column(Integer)
    governance_score_0_100 = Column(Integer)
    country_risk_0_100 = Column(Integer)
    collateral_coverage_pct = Column(Float)
    payment_incidents_12m = Column(Integer)
    
    # Additional financial fields (optional)
    ebit_margin_pct = Column(Float)
    interest_coverage = Column(Float)
    quick_ratio = Column(Float)
    cash_usd_m = Column(Float)
    total_assets_usd_m = Column(Float)
    equity_usd_m = Column(Float)
    net_debt_usd_m = Column(Float)
    interest_expense_usd_m = Column(Float)
    operating_cf_usd_m = Column(Float)
    capex_usd_m = Column(Float)
    fcf_usd_m = Column(Float)
    
    # Business information
    
    sector = Column(String(100))
    country = Column(String(100))
    ownership_type = Column(String(50))
    auditor_tier = Column(String(50))
    
    # Risk metrics
    pd_1y_pct = Column(Float)
    lgd_pct = Column(Float)
    ead_usd_m = Column(Float)
    risk_bucket = Column(String(20))
    implied_rating = Column(String(10))
    
    # Operational metrics
    dso_days = Column(Integer)
    dpo_days = Column(Integer)
    dio_days = Column(Integer)
    revenue_cagr_3y_pct = Column(Float)
    esg_controversies_3y = Column(Integer)
    fx_revenue_pct = Column(Integer)
    legal_disputes_open = Column(Integer)
    financials_audited = Column(Boolean)
    
    # String fields for enums/categories
    industry_cyclicality = Column(String(20))
    hedging_policy = Column(String(20))
    covenant_quality = Column(String(20))
    sanctions_exposure = Column(String(20))
    
    # Upload metadata
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    source_filename = Column(String(255))
    upload_batch_id = Column(String(100))
    
    def to_dict(self):
        """Convert SQLAlchemy model to dictionary"""
        return {
            'id': self.id,
            'entity_id': self.entity_id,
            'entity_name': self.entity_name,
            'debt_to_equity': self.debt_to_equity,
            'dscr': self.dscr,
            'current_ratio': self.current_ratio,
            'ebitda_margin_pct': self.ebitda_margin_pct,
            'revenue_usd_m': self.revenue_usd_m,
            'years_in_operation': self.years_in_operation,
            'governance_score_0_100': self.governance_score_0_100,
            'country_risk_0_100': self.country_risk_0_100,
            'collateral_coverage_pct': self.collateral_coverage_pct,
            'payment_incidents_12m': self.payment_incidents_12m,
            'ebit_margin_pct': self.ebit_margin_pct,
            'interest_coverage': self.interest_coverage,
            'quick_ratio': self.quick_ratio,
            'cash_usd_m': self.cash_usd_m,
            'total_assets_usd_m': self.total_assets_usd_m,
            'equity_usd_m': self.equity_usd_m,
            'net_debt_usd_m': self.net_debt_usd_m,
            'interest_expense_usd_m': self.interest_expense_usd_m,
            'operating_cf_usd_m': self.operating_cf_usd_m,
            'capex_usd_m': self.capex_usd_m,
            'fcf_usd_m': self.fcf_usd_m,
            'sector': self.sector,
            'country': self.country,
            'ownership_type': self.ownership_type,
            'auditor_tier': self.auditor_tier,
            'pd_1y_pct': self.pd_1y_pct,
            'lgd_pct': self.lgd_pct,
            'ead_usd_m': self.ead_usd_m,
            'risk_bucket': self.risk_bucket,
            'implied_rating': self.implied_rating,
            'dso_days': self.dso_days,
            'dpo_days': self.dpo_days,
            'dio_days': self.dio_days,
            'revenue_cagr_3y_pct': self.revenue_cagr_3y_pct,
            'esg_controversies_3y': self.esg_controversies_3y,
            'fx_revenue_pct': self.fx_revenue_pct,
            'legal_disputes_open': self.legal_disputes_open,
            'financials_audited': self.financials_audited,
            'industry_cyclicality': self.industry_cyclicality,
            'hedging_policy': self.hedging_policy,
            'covenant_quality': self.covenant_quality,
            'sanctions_exposure': self.sanctions_exposure,
            'upload_timestamp': self.upload_timestamp,
            'source_filename': self.source_filename,
            'upload_batch_id': self.upload_batch_id
        }

class ProcessingQueue(Base):
    __tablename__ = "processing_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Core identification
    entity_id = Column(String(50), index=True)
    entity_name = Column(String(200))
    
    # Financial metrics - essential fields from frontend
    debt_to_equity = Column(Float)
    dscr = Column(Float)  # Debt Service Coverage Ratio
    current_ratio = Column(Float)
    ebitda_margin_pct = Column(Float)
    revenue_usd_m = Column(Float)
    years_in_operation = Column(Integer)
    governance_score_0_100 = Column(Integer)
    country_risk_0_100 = Column(Integer)
    collateral_coverage_pct = Column(Float)
    payment_incidents_12m = Column(Integer)
    
    # Additional financial fields (optional)
    ebit_margin_pct = Column(Float)
    interest_coverage = Column(Float)
    quick_ratio = Column(Float)
    cash_usd_m = Column(Float)
    total_assets_usd_m = Column(Float)
    equity_usd_m = Column(Float)
    net_debt_usd_m = Column(Float)
    interest_expense_usd_m = Column(Float)
    operating_cf_usd_m = Column(Float)
    capex_usd_m = Column(Float)
    fcf_usd_m = Column(Float)
    
    # Business information
    sector = Column(String(100))
    country = Column(String(100))
    ownership_type = Column(String(50))
    auditor_tier = Column(String(50))
    
    # Risk metrics
    pd_1y_pct = Column(Float)
    lgd_pct = Column(Float)
    ead_usd_m = Column(Float)
    risk_bucket = Column(String(20))
    implied_rating = Column(String(10))
    
    # Operational metrics
    dso_days = Column(Integer)
    dpo_days = Column(Integer)
    dio_days = Column(Integer)
    revenue_cagr_3y_pct = Column(Float)
    esg_controversies_3y = Column(Integer)
    fx_revenue_pct = Column(Integer)
    legal_disputes_open = Column(Integer)
    financials_audited = Column(Boolean)
    
    # String fields for enums/categories
    industry_cyclicality = Column(String(20))
    hedging_policy = Column(String(20))
    covenant_quality = Column(String(20))
    sanctions_exposure = Column(String(20))
    
    # Upload metadata
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    source_filename = Column(String(255))
    upload_batch_id = Column(String(100))
    
    # NEW: Processing status column
    status = Column(String(50), default="unprocessed", index=True)
    processed_timestamp = Column(DateTime, nullable=True)
    processing_notes = Column(Text, nullable=True)
    
    def to_dict(self):
        """Convert SQLAlchemy model to dictionary"""
        return {
            'id': self.id,
            'entity_id': self.entity_id,
            'entity_name': self.entity_name,
            'debt_to_equity': self.debt_to_equity,
            'dscr': self.dscr,
            'current_ratio': self.current_ratio,
            'ebitda_margin_pct': self.ebitda_margin_pct,
            'revenue_usd_m': self.revenue_usd_m,
            'years_in_operation': self.years_in_operation,
            'governance_score_0_100': self.governance_score_0_100,
            'country_risk_0_100': self.country_risk_0_100,
            'collateral_coverage_pct': self.collateral_coverage_pct,
            'payment_incidents_12m': self.payment_incidents_12m,
            'ebit_margin_pct': self.ebit_margin_pct,
            'interest_coverage': self.interest_coverage,
            'quick_ratio': self.quick_ratio,
            'cash_usd_m': self.cash_usd_m,
            'total_assets_usd_m': self.total_assets_usd_m,
            'equity_usd_m': self.equity_usd_m,
            'net_debt_usd_m': self.net_debt_usd_m,
            'interest_expense_usd_m': self.interest_expense_usd_m,
            'operating_cf_usd_m': self.operating_cf_usd_m,
            'capex_usd_m': self.capex_usd_m,
            'fcf_usd_m': self.fcf_usd_m,
            'sector': self.sector,
            'country': self.country,
            'ownership_type': self.ownership_type,
            'auditor_tier': self.auditor_tier,
            'pd_1y_pct': self.pd_1y_pct,
            'lgd_pct': self.lgd_pct,
            'ead_usd_m': self.ead_usd_m,
            'risk_bucket': self.risk_bucket,
            'implied_rating': self.implied_rating,
            'dso_days': self.dso_days,
            'dpo_days': self.dpo_days,
            'dio_days': self.dio_days,
            'revenue_cagr_3y_pct': self.revenue_cagr_3y_pct,
            'esg_controversies_3y': self.esg_controversies_3y,
            'fx_revenue_pct': self.fx_revenue_pct,
            'legal_disputes_open': self.legal_disputes_open,
            'financials_audited': self.financials_audited,
            'industry_cyclicality': self.industry_cyclicality,
            'hedging_policy': self.hedging_policy,
            'covenant_quality': self.covenant_quality,
            'sanctions_exposure': self.sanctions_exposure,
            'upload_timestamp': self.upload_timestamp,
            'source_filename': self.source_filename,
            'upload_batch_id': self.upload_batch_id,
            'status': self.status,
            'processed_timestamp': self.processed_timestamp,
            'processing_notes': self.processing_notes
        }

class DashboardStats(Base):
    __tablename__ = "dashboard_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Main Dashboard Metrics
    total_applications_processed = Column(Integer, default=0)
    total_accepted = Column(Integer, default=0)
    under_review_manual = Column(Integer, default=0)
    total_rejected = Column(Integer, default=0)
    
    # Percentage calculations (will be auto-calculated)
    accepted_percentage = Column(Float, default=0.0)
    under_review_percentage = Column(Float, default=0.0)
    rejected_percentage = Column(Float, default=0.0)
    
    # Portfolio Risk Distribution
    low_risk_count = Column(Integer, default=0)
    moderate_risk_count = Column(Integer, default=0)
    high_risk_count = Column(Integer, default=0)
    
    # Risk Distribution Percentages (will be auto-calculated)
    low_risk_percentage = Column(Float, default=0.0)
    moderate_risk_percentage = Column(Float, default=0.0)
    high_risk_percentage = Column(Float, default=0.0)
    
    # System Status
    status_check = Column(String(20), default="OK")
    
    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(100), default="system")
    
    def to_dict(self):
        """Convert SQLAlchemy model to dictionary"""
        return {
            'id': self.id,
            'total_applications_processed': self.total_applications_processed,
            'total_accepted': self.total_accepted,
            'under_review_manual': self.under_review_manual,
            'total_rejected': self.total_rejected,
            'accepted_percentage': self.accepted_percentage,
            'under_review_percentage': self.under_review_percentage,
            'rejected_percentage': self.rejected_percentage,
            'low_risk_count': self.low_risk_count,
            'moderate_risk_count': self.moderate_risk_count,
            'high_risk_count': self.high_risk_count,
            'low_risk_percentage': self.low_risk_percentage,
            'moderate_risk_percentage': self.moderate_risk_percentage,
            'high_risk_percentage': self.high_risk_percentage,
            'status_check': self.status_check,
            'last_updated': self.last_updated,
            'updated_by': self.updated_by
        }
    
    def calculate_percentages(self):
        """Calculate percentages based on totals"""
        total = self.total_applications_processed
        if total > 0:
            self.accepted_percentage = round((self.total_accepted / total) * 100, 1)
            self.under_review_percentage = round((self.under_review_manual / total) * 100, 1)
            self.rejected_percentage = round((self.total_rejected / total) * 100, 1)
            
            # Risk distribution percentages
            risk_total = self.low_risk_count + self.moderate_risk_count + self.high_risk_count
            if risk_total > 0:
                self.low_risk_percentage = round((self.low_risk_count / risk_total) * 100, 1)
                self.moderate_risk_percentage = round((self.moderate_risk_count / risk_total) * 100, 1)
                self.high_risk_percentage = round((self.high_risk_count / risk_total) * 100, 1)

# Database setup
def get_database_url():
    """Get the SQLite database URL"""
    db_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # Go up to backend/
    db_path = os.path.join(db_dir, "credit_risk.db")
    return f"sqlite:///{db_path}"

def create_database_engine():
    """Create SQLAlchemy engine"""
    database_url = get_database_url()
    engine = create_engine(database_url, echo=True)  # echo=True for debugging
    return engine

def get_session():
    """Get database session"""
    engine = create_database_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def init_database():
    """Initialize database tables"""
    engine = create_database_engine()
    Base.metadata.create_all(bind=engine)
    return engine