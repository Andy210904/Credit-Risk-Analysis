from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import uuid
import logging

from ..models.database import ClientData, ProcessingQueue, DashboardStats, get_session, init_database

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Ensure the database and tables exist"""
        try:
            init_database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def save_csv_data(self, csv_data: List[Dict[str, Any]], filename: str) -> Dict[str, Any]:
        """Save CSV data to database"""
        session = get_session()
        batch_id = str(uuid.uuid4())
        saved_count = 0
        errors = []
        
        try:
            for row_index, row_data in enumerate(csv_data):
                try:
                    # Create ClientData instance
                    client = ClientData(
                        entity_id=str(row_data.get('entity_id', f'CLIENT_{batch_id[:8]}_{row_index}')),
                        entity_name=str(row_data.get('entity_name', f'Client {row_index + 1}')),
                        
                        # Essential financial metrics
                        debt_to_equity=self._safe_float(row_data.get('debt_to_equity')),
                        dscr=self._safe_float(row_data.get('dscr')),
                        current_ratio=self._safe_float(row_data.get('current_ratio')),
                        ebitda_margin_pct=self._safe_float(row_data.get('ebitda_margin_pct')),
                        revenue_usd_m=self._safe_float(row_data.get('revenue_usd_m')),
                        years_in_operation=self._safe_int(row_data.get('years_in_operation')),
                        governance_score_0_100=self._safe_int(row_data.get('governance_score_0_100')),
                        country_risk_0_100=self._safe_int(row_data.get('country_risk_0_100')),
                        collateral_coverage_pct=self._safe_float(row_data.get('collateral_coverage_pct')),
                        payment_incidents_12m=self._safe_int(row_data.get('payment_incidents_12m')),
                        
                        # Additional financial fields
                        ebit_margin_pct=self._safe_float(row_data.get('ebit_margin_pct')),
                        interest_coverage=self._safe_float(row_data.get('interest_coverage')),
                        quick_ratio=self._safe_float(row_data.get('quick_ratio')),
                        cash_usd_m=self._safe_float(row_data.get('cash_usd_m')),
                        total_assets_usd_m=self._safe_float(row_data.get('total_assets_usd_m')),
                        equity_usd_m=self._safe_float(row_data.get('equity_usd_m')),
                        net_debt_usd_m=self._safe_float(row_data.get('net_debt_usd_m')),
                        interest_expense_usd_m=self._safe_float(row_data.get('interest_expense_usd_m')),
                        operating_cf_usd_m=self._safe_float(row_data.get('operating_cf_usd_m')),
                        capex_usd_m=self._safe_float(row_data.get('capex_usd_m')),
                        fcf_usd_m=self._safe_float(row_data.get('fcf_usd_m')),
                        
                        # Business information
                        sector=self._safe_string(row_data.get('sector')),
                        country=self._safe_string(row_data.get('country')),
                        ownership_type=self._safe_string(row_data.get('ownership_type')),
                        auditor_tier=self._safe_string(row_data.get('auditor_tier')),
                        
                        # Risk metrics
                        pd_1y_pct=self._safe_float(row_data.get('pd_1y_pct')),
                        lgd_pct=self._safe_float(row_data.get('lgd_pct')),
                        ead_usd_m=self._safe_float(row_data.get('ead_usd_m')),
                        risk_bucket=self._safe_string(row_data.get('risk_bucket')),
                        implied_rating=self._safe_string(row_data.get('implied_rating')),
                        
                        # Operational metrics
                        dso_days=self._safe_int(row_data.get('dso_days')),
                        dpo_days=self._safe_int(row_data.get('dpo_days')),
                        dio_days=self._safe_int(row_data.get('dio_days')),
                        revenue_cagr_3y_pct=self._safe_float(row_data.get('revenue_cagr_3y_pct')),
                        esg_controversies_3y=self._safe_int(row_data.get('esg_controversies_3y')),
                        fx_revenue_pct=self._safe_int(row_data.get('fx_revenue_pct')),
                        legal_disputes_open=self._safe_int(row_data.get('legal_disputes_open')),
                        financials_audited=self._safe_bool(row_data.get('financials_audited')),
                        
                        # String fields for enums/categories
                        industry_cyclicality=self._safe_string(row_data.get('industry_cyclicality')),
                        hedging_policy=self._safe_string(row_data.get('hedging_policy')),
                        covenant_quality=self._safe_string(row_data.get('covenant_quality')),
                        sanctions_exposure=self._safe_string(row_data.get('sanctions_exposure')),
                        
                        # Metadata
                        source_filename=filename,
                        upload_batch_id=batch_id,
                        upload_timestamp=datetime.utcnow()
                    )
                    
                    session.add(client)
                    saved_count += 1
                    
                except Exception as e:
                    error_msg = f"Row {row_index + 1}: {str(e)}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
            
            session.commit()
            logger.info(f"Saved {saved_count} client records to database")
            
            return {
                "success": True,
                "batch_id": batch_id,
                "saved_count": saved_count,
                "total_rows": len(csv_data),
                "errors": errors
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving CSV data to database: {e}")
            raise
        finally:
            session.close()
    
    def get_all_clients(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all client data from database"""
        session = get_session()
        try:
            query = session.query(ClientData).order_by(ClientData.upload_timestamp.desc())
            if limit:
                query = query.limit(limit)
            
            clients = query.all()
            return [client.to_dict() for client in clients]
            
        except Exception as e:
            logger.error(f"Error retrieving clients from database: {e}")
            raise
        finally:
            session.close()
    
    def get_clients_by_batch(self, batch_id: str) -> List[Dict[str, Any]]:
        """Get clients by batch ID"""
        session = get_session()
        try:
            clients = session.query(ClientData).filter(ClientData.upload_batch_id == batch_id).all()
            return [client.to_dict() for client in clients]
        except Exception as e:
            logger.error(f"Error retrieving clients by batch {batch_id}: {e}")
            raise
        finally:
            session.close()
    
    def clear_all_data(self) -> Dict[str, Any]:
        """Clear all client data from database"""
        session = get_session()
        try:
            deleted_count = session.query(ClientData).delete()
            session.commit()
            logger.info(f"Deleted {deleted_count} client records from database")
            return {"success": True, "deleted_count": deleted_count}
        except Exception as e:
            session.rollback()
            logger.error(f"Error clearing database: {e}")
            raise
        finally:
            session.close()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        session = get_session()
        try:
            total_clients = session.query(ClientData).count()
            
            # Get recent batches
            recent_batches = session.execute(
                text("""
                SELECT upload_batch_id, source_filename, upload_timestamp, COUNT(*) as client_count
                FROM client_data 
                GROUP BY upload_batch_id, source_filename, upload_timestamp
                ORDER BY upload_timestamp DESC 
                LIMIT 10
                """)
            ).fetchall()
            
            return {
                "total_clients": total_clients,
                "recent_batches": [
                    {
                        "batch_id": batch.upload_batch_id,
                        "filename": batch.source_filename,
                        "upload_time": batch.upload_timestamp,
                        "client_count": batch.client_count
                    }
                    for batch in recent_batches
                ]
            }
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            raise
        finally:
            session.close()
    
    # ===== PROCESSING QUEUE METHODS =====
    
    def save_csv_to_processing_queue(self, csv_data: List[Dict[str, Any]], filename: str) -> Dict[str, Any]:
        """Save CSV data to processing queue with 'unprocessed' status"""
        session = get_session()
        batch_id = str(uuid.uuid4())
        saved_count = 0
        errors = []
        
        try:
            for row_index, row_data in enumerate(csv_data):
                try:
                    # Create ProcessingQueue instance
                    processing_item = ProcessingQueue(
                        entity_id=str(row_data.get('entity_id', f'CLIENT_{batch_id[:8]}_{row_index}')),
                        entity_name=str(row_data.get('entity_name', f'Client {row_index + 1}')),
                        
                        # Essential financial metrics
                        debt_to_equity=self._safe_float(row_data.get('debt_to_equity')),
                        dscr=self._safe_float(row_data.get('dscr')),
                        current_ratio=self._safe_float(row_data.get('current_ratio')),
                        ebitda_margin_pct=self._safe_float(row_data.get('ebitda_margin_pct')),
                        revenue_usd_m=self._safe_float(row_data.get('revenue_usd_m')),
                        years_in_operation=self._safe_int(row_data.get('years_in_operation')),
                        governance_score_0_100=self._safe_int(row_data.get('governance_score_0_100')),
                        country_risk_0_100=self._safe_int(row_data.get('country_risk_0_100')),
                        collateral_coverage_pct=self._safe_float(row_data.get('collateral_coverage_pct')),
                        payment_incidents_12m=self._safe_int(row_data.get('payment_incidents_12m')),
                        
                        # Additional financial fields
                        ebit_margin_pct=self._safe_float(row_data.get('ebit_margin_pct')),
                        interest_coverage=self._safe_float(row_data.get('interest_coverage')),
                        quick_ratio=self._safe_float(row_data.get('quick_ratio')),
                        cash_usd_m=self._safe_float(row_data.get('cash_usd_m')),
                        total_assets_usd_m=self._safe_float(row_data.get('total_assets_usd_m')),
                        equity_usd_m=self._safe_float(row_data.get('equity_usd_m')),
                        net_debt_usd_m=self._safe_float(row_data.get('net_debt_usd_m')),
                        interest_expense_usd_m=self._safe_float(row_data.get('interest_expense_usd_m')),
                        operating_cf_usd_m=self._safe_float(row_data.get('operating_cf_usd_m')),
                        capex_usd_m=self._safe_float(row_data.get('capex_usd_m')),
                        fcf_usd_m=self._safe_float(row_data.get('fcf_usd_m')),
                        
                        # Business information
                        sector=self._safe_string(row_data.get('sector')),
                        country=self._safe_string(row_data.get('country')),
                        ownership_type=self._safe_string(row_data.get('ownership_type')),
                        auditor_tier=self._safe_string(row_data.get('auditor_tier')),
                        
                        # Risk metrics
                        pd_1y_pct=self._safe_float(row_data.get('pd_1y_pct')),
                        lgd_pct=self._safe_float(row_data.get('lgd_pct')),
                        ead_usd_m=self._safe_float(row_data.get('ead_usd_m')),
                        risk_bucket=self._safe_string(row_data.get('risk_bucket')),
                        implied_rating=self._safe_string(row_data.get('implied_rating')),
                        
                        # Operational metrics
                        dso_days=self._safe_int(row_data.get('dso_days')),
                        dpo_days=self._safe_int(row_data.get('dpo_days')),
                        dio_days=self._safe_int(row_data.get('dio_days')),
                        revenue_cagr_3y_pct=self._safe_float(row_data.get('revenue_cagr_3y_pct')),
                        esg_controversies_3y=self._safe_int(row_data.get('esg_controversies_3y')),
                        fx_revenue_pct=self._safe_int(row_data.get('fx_revenue_pct')),
                        legal_disputes_open=self._safe_int(row_data.get('legal_disputes_open')),
                        financials_audited=self._safe_bool(row_data.get('financials_audited')),
                        
                        # String fields for enums/categories
                        industry_cyclicality=self._safe_string(row_data.get('industry_cyclicality')),
                        hedging_policy=self._safe_string(row_data.get('hedging_policy')),
                        covenant_quality=self._safe_string(row_data.get('covenant_quality')),
                        sanctions_exposure=self._safe_string(row_data.get('sanctions_exposure')),
                        
                        # Metadata
                        source_filename=filename,
                        upload_batch_id=batch_id,
                        upload_timestamp=datetime.utcnow(),
                        
                        # Status (default is 'unprocessed')
                        status="unprocessed"
                    )
                    
                    session.add(processing_item)
                    saved_count += 1
                    
                except Exception as e:
                    error_msg = f"Row {row_index + 1}: {str(e)}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
            
            session.commit()
            logger.info(f"Saved {saved_count} client records to processing queue")
            
            return {
                "success": True,
                "batch_id": batch_id,
                "saved_count": saved_count,
                "total_rows": len(csv_data),
                "errors": errors
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving CSV data to processing queue: {e}")
            raise
        finally:
            session.close()
    
    def get_processing_queue_items(self, status: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get items from processing queue, optionally filtered by status"""
        session = get_session()
        try:
            query = session.query(ProcessingQueue).order_by(ProcessingQueue.upload_timestamp.desc())
            
            if status:
                query = query.filter(ProcessingQueue.status == status)
            
            if limit:
                query = query.limit(limit)
            
            items = query.all()
            return [item.to_dict() for item in items]
            
        except Exception as e:
            logger.error(f"Error retrieving processing queue items: {e}")
            raise
        finally:
            session.close()
    
    def update_processing_status(self, item_id: int, new_status: str, notes: Optional[str] = None) -> bool:
        """Update the processing status of a queue item"""
        session = get_session()
        try:
            item = session.query(ProcessingQueue).filter(ProcessingQueue.id == item_id).first()
            if not item:
                logger.warning(f"Processing queue item {item_id} not found")
                return False
            
            item.status = new_status
            item.processed_timestamp = datetime.utcnow()
            if notes:
                item.processing_notes = notes
            
            session.commit()
            logger.info(f"Updated processing queue item {item_id} status to {new_status}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating processing status for item {item_id}: {e}")
            raise
        finally:
            session.close()
    
    def get_processing_queue_stats(self) -> Dict[str, Any]:
        """Get processing queue statistics"""
        session = get_session()
        try:
            total_items = session.query(ProcessingQueue).count()
            
            # Count by status
            status_counts = {}
            status_results = session.execute(
                text("SELECT status, COUNT(*) FROM processing_queue GROUP BY status")
            ).fetchall()
            
            for status, count in status_results:
                status_counts[status] = count
            
            return {
                "total_items": total_items,
                "status_counts": status_counts,
                "unprocessed_count": status_counts.get("unprocessed", 0),
                "processed_count": status_counts.get("processed", 0),
                "failed_count": status_counts.get("failed", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting processing queue stats: {e}")
            raise
        finally:
            session.close()
    
    def clear_processing_queue(self) -> Dict[str, Any]:
        """Clear all items from processing queue"""
        session = get_session()
        try:
            deleted_count = session.query(ProcessingQueue).delete()
            session.commit()
            logger.info(f"Deleted {deleted_count} items from processing queue")
            return {"success": True, "deleted_count": deleted_count}
        except Exception as e:
            session.rollback()
            logger.error(f"Error clearing processing queue: {e}")
            raise
        finally:
            session.close()
    
    # ===== DASHBOARD STATISTICS METHODS =====
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get current dashboard statistics"""
        session = get_session()
        try:
            # Get the latest stats record
            stats = session.query(DashboardStats).order_by(DashboardStats.last_updated.desc()).first()

            # Determine actual totals from client_data
            actual_total = session.query(ClientData).count()

            # Conditions under which we should rebuild stats from real data:
            # 1. No stats row exists
            # 2. Stats row is the original placeholder sample (150) but actual_total differs
            # 3. Stats total does not match current client_data count (e.g., new uploads)
            needs_refresh = False
            if not stats:
                needs_refresh = True
            else:
                placeholder_sample = stats.total_applications_processed == 150 and stats.updated_by == 'system_initialization'
                if placeholder_sample and actual_total != 150:
                    needs_refresh = True
                elif stats.total_applications_processed != actual_total:
                    # If there is a mismatch greater than zero clients we refresh to reflect reality
                    needs_refresh = True

            if needs_refresh:
                # Build fresh stats from real data (uses existing helper)
                refreshed = self.refresh_dashboard_stats_from_data()
                return refreshed

            return stats.to_dict()
            
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            raise
        finally:
            session.close()
    
    def create_default_dashboard_stats(self) -> Dict[str, Any]:
        """Create default dashboard statistics with sample data"""
        session = get_session()
        try:
            # Sample data based on the dashboard image
            default_stats = DashboardStats(
                total_applications_processed=150,
                total_accepted=65,
                under_review_manual=25,
                total_rejected=60,
                
                low_risk_count=45,
                moderate_risk_count=15,
                high_risk_count=5,
                
                status_check="OK",
                updated_by="system_initialization"
            )
            
            # Calculate percentages
            default_stats.calculate_percentages()
            
            session.add(default_stats)
            session.commit()
            
            # Refresh the object to get the ID assigned by the database
            session.refresh(default_stats)
            
            # Convert to dict while session is still active
            stats_dict = default_stats.to_dict()
            
            logger.info("Created default dashboard statistics")
            return stats_dict
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating default dashboard stats: {e}")
            raise
        finally:
            session.close()
    
    def update_dashboard_stats(self, stats_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update dashboard statistics"""
        session = get_session()
        try:
            # Get existing stats or create new
            stats = session.query(DashboardStats).order_by(DashboardStats.last_updated.desc()).first()
            
            if not stats:
                stats = DashboardStats()
                session.add(stats)
            
            # Update fields from input data
            for key, value in stats_data.items():
                if hasattr(stats, key):
                    setattr(stats, key, value)
            
            # Update metadata
            stats.last_updated = datetime.utcnow()
            stats.updated_by = stats_data.get('updated_by', 'api_update')
            
            # Calculate percentages
            stats.calculate_percentages()
            
            session.commit()
            logger.info("Updated dashboard statistics")
            
            return stats.to_dict()
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating dashboard stats: {e}")
            raise
        finally:
            session.close()
    
    def refresh_dashboard_stats_from_data(self) -> Dict[str, Any]:
        """Refresh dashboard statistics based on actual client data"""
        session = get_session()
        try:
            # Count applications by risk bucket
            risk_counts = session.execute(
                text("""
                SELECT risk_bucket, COUNT(*) as count 
                FROM client_data 
                WHERE risk_bucket IS NOT NULL 
                GROUP BY risk_bucket
                """)
            ).fetchall()
            
            # Initialize counts
            low_risk = moderate_risk = high_risk = 0
            
            for risk_bucket, count in risk_counts:
                risk_lower = risk_bucket.lower()
                if 'low' in risk_lower or 'green' in risk_lower:
                    low_risk += count
                elif 'moderate' in risk_lower or 'amber' in risk_lower or 'medium' in risk_lower:
                    moderate_risk += count
                elif 'high' in risk_lower or 'red' in risk_lower:
                    high_risk += count
            
            total_processed = session.query(ClientData).count()
            
            # For demo purposes, distribute the applications
            # In real scenario, you'd have actual status fields
            total_accepted = int(total_processed * 0.43)  # ~43% acceptance rate
            under_review = int(total_processed * 0.17)    # ~17% under review
            total_rejected = total_processed - total_accepted - under_review
            
            # Update or create stats
            stats_data = {
                "total_applications_processed": total_processed,
                "total_accepted": total_accepted,
                "under_review_manual": under_review,
                "total_rejected": total_rejected,
                "low_risk_count": low_risk,
                "moderate_risk_count": moderate_risk,
                "high_risk_count": high_risk,
                "status_check": "OK",
                "updated_by": "auto_refresh"
            }
            
            return self.update_dashboard_stats(stats_data)
            
        except Exception as e:
            logger.error(f"Error refreshing dashboard stats from data: {e}")
            raise
        finally:
            session.close()
    
    # ===== HELPER METHODS =====
    
    def _safe_float(self, value: Any) -> Optional[float]:
        """Safely convert value to float"""
        if value is None or value == '' or str(value).lower() in ['nan', 'null', 'none']:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value: Any) -> Optional[int]:
        """Safely convert value to int"""
        if value is None or value == '' or str(value).lower() in ['nan', 'null', 'none']:
            return None
        try:
            return int(float(value))  # Convert through float to handle "1.0" -> 1
        except (ValueError, TypeError):
            return None
    
    def _safe_string(self, value: Any) -> Optional[str]:
        """Safely convert value to string"""
        if value is None or str(value).lower() in ['nan', 'null', 'none', '']:
            return None
        return str(value).strip()
    
    def _safe_bool(self, value: Any) -> Optional[bool]:
        """Safely convert value to bool"""
        if value is None or value == '' or str(value).lower() in ['nan', 'null', 'none']:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'y', 'on']
        try:
            return bool(int(value))
        except (ValueError, TypeError):
            return None

# Global database service instance
database_service = DatabaseService()