import pandas as pd
import os
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from app.models.data import (
    CreditEntity, RiskBucket, Sector, OwnershipType, AuditorTier, 
    IndustryCyclicality, HedgingPolicy, CovenantQuality, SanctionsExposure
)
import logging

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self):
        self.csv_path = "data/credit_risk_dataset_50_entities.csv"  # Fallback default file
        self.df = None
        self.data_source = "none"
        # Try to load default data, but don't fail if not found
        self._load_default_data()
    
    def _load_default_data(self):
        """Load default CSV data if available (optional)"""
        try:
            if os.path.exists(self.csv_path):
                self.df = pd.read_csv(self.csv_path)
                self.data_source = "default_file"
                logger.info(f"Loaded {len(self.df)} records from default CSV file")
            else:
                logger.info("No default CSV file found. Waiting for file upload.")
                self.data_source = "none"
        except Exception as e:
            logger.warning(f"Could not load default CSV data: {str(e)}")
            self.data_source = "none"
    
    def load_from_dataframe(self, df: pd.DataFrame) -> bool:
        """Load data from uploaded pandas DataFrame"""
        try:
            self.df = df.copy()
            self.data_source = "uploaded_file"
            logger.info(f"Loaded {len(self.df)} records from uploaded DataFrame")
            return True
        except Exception as e:
            logger.error(f"Error loading DataFrame: {str(e)}")
            return False
    
    def get_data_status(self) -> Dict[str, Any]:
        """Get current data loading status"""
        return {
            "has_data": self.df is not None and not self.df.empty,
            "total_entities": len(self.df) if self.df is not None else 0,
            "source": self.data_source,
            "columns": list(self.df.columns) if self.df is not None else []
        }
    
    def clear_data(self):
        """Clear all loaded data"""
        self.df = None
        self.data_source = "none"
        logger.info("All data cleared from memory")
    
    def _check_data_loaded(self):
        """Check if data is loaded, raise exception if not"""
        if self.df is None or self.df.empty:
            raise HTTPException(
                status_code=400, 
                detail="No data available. Please upload a CSV file first using the /upload-csv endpoint."
            )
    
    def _row_to_entity(self, row) -> CreditEntity:
        """Convert pandas row to CreditEntity model"""
        # Handle None values for sanctions_exposure
        sanctions_exposure = None
        if pd.notna(row['sanctions_exposure']) and row['sanctions_exposure'] != 'None':
            sanctions_exposure = SanctionsExposure(row['sanctions_exposure'])
            
        # Handle NaN values for hedging_policy
        hedging_policy = HedgingPolicy.NONE
        if pd.notna(row['hedging_policy']) and str(row['hedging_policy']).lower() != 'nan':
            hedging_policy_value = str(row['hedging_policy']).title()  # Convert to proper case
            hedging_policy = HedgingPolicy(hedging_policy_value)
        
        return CreditEntity(
            entity_id=str(row['entity_id']),
            entity_name=str(row['entity_name']),
            sector=Sector(row['sector']),
            country=str(row['country']),
            revenue_usd_m=float(row['revenue_usd_m']),
            ebitda_margin_pct=float(row['ebitda_margin_pct']),
            ebit_margin_pct=float(row['ebit_margin_pct']),
            cash_usd_m=float(row['cash_usd_m']),
            total_assets_usd_m=float(row['total_assets_usd_m']),
            equity_usd_m=float(row['equity_usd_m']),
            net_debt_usd_m=float(row['net_debt_usd_m']),
            debt_to_equity=float(row['debt_to_equity']),
            interest_expense_usd_m=float(row['interest_expense_usd_m']),
            interest_coverage=float(row['interest_coverage']),
            operating_cf_usd_m=float(row['operating_cf_usd_m']),
            capex_usd_m=float(row['capex_usd_m']),
            fcf_usd_m=float(row['fcf_usd_m']),
            dscr=float(row['dscr']),
            current_ratio=float(row['current_ratio']),
            quick_ratio=float(row['quick_ratio']),
            dso_days=int(row['dso_days']),
            dpo_days=int(row['dpo_days']),
            dio_days=int(row['dio_days']),
            revenue_cagr_3y_pct=float(row['revenue_cagr_3y_pct']),
            years_in_operation=int(row['years_in_operation']),
            ownership_type=OwnershipType(row['ownership_type']),
            auditor_tier=AuditorTier(row['auditor_tier']),
            governance_score_0_100=int(row['governance_score_0_100']),
            esg_controversies_3y=int(row['esg_controversies_3y']),
            country_risk_0_100=int(row['country_risk_0_100']),
            industry_cyclicality=IndustryCyclicality(row['industry_cyclicality']),
            fx_revenue_pct=int(row['fx_revenue_pct']),
            hedging_policy=hedging_policy,
            collateral_coverage_pct=int(row['collateral_coverage_pct']),
            covenant_quality=CovenantQuality(row['covenant_quality']),
            payment_incidents_12m=int(row['payment_incidents_12m']),
            legal_disputes_open=int(row['legal_disputes_open']),
            sanctions_exposure=sanctions_exposure,
            financials_audited=bool(row['financials_audited'] == 'Yes'),
            pd_1y_pct=float(row['PD_1y_pct']),
            lgd_pct=float(row['LGD_pct']),
            ead_usd_m=float(row['EAD_usd_m']),
            risk_bucket=RiskBucket(row['risk_bucket']),
            implied_rating=str(row['implied_rating'])
        )
    
    def get_all_entities(self) -> List[CreditEntity]:
        """Get all credit entities from loaded data"""
        try:
            self._check_data_loaded()
            
            entities = []
            for _, row in self.df.iterrows():
                entity = self._row_to_entity(row)
                entities.append(entity)
            
            return entities
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting all entities: {str(e)}")
            raise
    
    def get_entity_by_id(self, entity_id: str) -> Optional[CreditEntity]:
        """Get a specific credit entity by ID"""
        try:
            self._check_data_loaded()
            
            row = self.df[self.df['entity_id'] == entity_id]
            if row.empty:
                return None
            
            return self._row_to_entity(row.iloc[0])
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting entity by ID {entity_id}: {str(e)}")
            raise
    
    def get_entities_by_risk_bucket(self, risk_bucket: RiskBucket) -> List[CreditEntity]:
        """Get entities filtered by risk bucket"""
        try:
            self._check_data_loaded()
            
            filtered_df = self.df[self.df['risk_bucket'] == risk_bucket.value]
            entities = []
            
            for _, row in filtered_df.iterrows():
                entity = self._row_to_entity(row)
                entities.append(entity)
            
            return entities
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error filtering by risk bucket {risk_bucket}: {str(e)}")
            raise
    
    def get_entities_by_sector(self, sector: Sector) -> List[CreditEntity]:
        """Get entities filtered by sector"""
        try:
            self._check_data_loaded()
            
            filtered_df = self.df[self.df['sector'] == sector.value]
            entities = []
            
            for _, row in filtered_df.iterrows():
                entity = self._row_to_entity(row)
                entities.append(entity)
            
            return entities
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error filtering by sector {sector}: {str(e)}")
            raise
    
    def get_entities_by_country(self, country: str) -> List[CreditEntity]:
        """Get entities filtered by country"""
        try:
            self._check_data_loaded()
            
            filtered_df = self.df[self.df['country'].str.lower() == country.lower()]
            entities = []
            
            for _, row in filtered_df.iterrows():
                entity = self._row_to_entity(row)
                entities.append(entity)
            
            return entities
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error filtering by country {country}: {str(e)}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the credit entities"""
        try:
            self._check_data_loaded()
            
            total_count = len(self.df)
            risk_counts = self.df['risk_bucket'].value_counts().to_dict()
            sector_counts = self.df['sector'].value_counts().to_dict()
            country_counts = self.df['country'].value_counts().to_dict()
            
            # Calculate averages
            avg_revenue = self.df['revenue_usd_m'].mean()
            avg_ebitda_margin = self.df['ebitda_margin_pct'].mean()
            avg_pd = self.df['PD_1y_pct'].mean()
            avg_assets = self.df['total_assets_usd_m'].mean()
            
            return {
                "total_entities": total_count,
                "risk_distribution": risk_counts,
                "sector_distribution": sector_counts,
                "country_distribution": country_counts,
                "averages": {
                    "revenue_usd_m": round(avg_revenue, 2),
                    "ebitda_margin_pct": round(avg_ebitda_margin, 2),
                    "pd_1y_pct": round(avg_pd, 2),
                    "total_assets_usd_m": round(avg_assets, 2)
                },
                "risk_metrics": {
                    "high_risk_count": risk_counts.get('High', 0),
                    "medium_risk_count": risk_counts.get('Medium', 0),
                    "low_risk_count": risk_counts.get('Low', 0)
                }
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error calculating statistics: {str(e)}")
            raise
    
    def search_entities(self, 
                       min_revenue: Optional[float] = None,
                       max_revenue: Optional[float] = None,
                       min_pd: Optional[float] = None,
                       max_pd: Optional[float] = None,
                       risk_bucket: Optional[RiskBucket] = None,
                       sector: Optional[Sector] = None,
                       country: Optional[str] = None,
                       ownership_type: Optional[OwnershipType] = None) -> List[CreditEntity]:
        """Search entities with multiple filters"""
        try:
            self._check_data_loaded()
            
            filtered_df = self.df.copy()
            
            if min_revenue is not None:
                filtered_df = filtered_df[filtered_df['revenue_usd_m'] >= min_revenue]
            
            if max_revenue is not None:
                filtered_df = filtered_df[filtered_df['revenue_usd_m'] <= max_revenue]
            
            if min_pd is not None:
                filtered_df = filtered_df[filtered_df['PD_1y_pct'] >= min_pd]
            
            if max_pd is not None:
                filtered_df = filtered_df[filtered_df['PD_1y_pct'] <= max_pd]
            
            if risk_bucket is not None:
                filtered_df = filtered_df[filtered_df['risk_bucket'] == risk_bucket.value]
            
            if sector is not None:
                filtered_df = filtered_df[filtered_df['sector'] == sector.value]
            
            if country is not None:
                filtered_df = filtered_df[filtered_df['country'].str.lower() == country.lower()]
                
            if ownership_type is not None:
                filtered_df = filtered_df[filtered_df['ownership_type'] == ownership_type.value]
            
            entities = []
            for _, row in filtered_df.iterrows():
                entity = self._row_to_entity(row)
                entities.append(entity)
            
            return entities
        except Exception as e:
            logger.error(f"Error searching entities: {str(e)}")
            raise
    
    def get_top_entities_by_revenue(self, limit: int = 10) -> List[CreditEntity]:
        """Get top entities by revenue"""
        try:
            self._check_data_loaded()
            
            top_df = self.df.nlargest(limit, 'revenue_usd_m')
            entities = []
            
            for _, row in top_df.iterrows():
                entity = self._row_to_entity(row)
                entities.append(entity)
            
            return entities
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting top entities by revenue: {str(e)}")
            raise
    
    def get_entities_by_rating_range(self, min_rating: str, max_rating: str) -> List[CreditEntity]:
        """Get entities within a credit rating range"""
        try:
            self._check_data_loaded()
            
            # This is a simplified rating comparison - you might want to implement proper rating ordering
            filtered_df = self.df[
                (self.df['implied_rating'] >= min_rating) & 
                (self.df['implied_rating'] <= max_rating)
            ]
            
            entities = []
            for _, row in filtered_df.iterrows():
                entity = self._row_to_entity(row)
                entities.append(entity)
            
            return entities
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error filtering by rating range: {str(e)}")
            raise