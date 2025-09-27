from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import pandas as pd
import io
import logging
from app.services.data_service import DataService
from app.services.database_service import database_service
from app.routers.data import clean_for_json

router = APIRouter()
data_service = DataService()
logger = logging.getLogger(__name__)

@router.post("/upload-csv")
async def frontend_upload_csv(file: UploadFile = File(...)):
    """
    CSV upload endpoint specifically for frontend integration
    Saves data to SQLite database instead of files
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")

        # Read file content
        content = await file.read()
        
        # Parse CSV
        try:
            df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')
        except Exception as parse_error:
            try:
                df = pd.read_csv(io.BytesIO(content), encoding='latin-1')
            except Exception as encoding_error:
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not parse CSV file: {encoding_error}"
                )

        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")

        logger.info(f"CSV loaded: {df.shape[0]} rows, {df.shape[1]} columns")

        # Convert DataFrame to list of dictionaries
        clients_data = []
        for _, row in df.iterrows():
            client = {}
            for col in df.columns:
                value = row[col]
                # Handle NaN values
                if pd.isna(value):
                    client[col] = None
                elif isinstance(value, (int, float)):
                    client[col] = float(value) if not pd.isna(value) else None
                else:
                    client[col] = str(value)
            clients_data.append(client)

        # Save to database instead of file
        db_result = database_service.save_csv_data(clients_data, file.filename)
        
        if not db_result["success"]:
            raise HTTPException(status_code=500, detail="Failed to save data to database")

        logger.info(f"Saved {db_result['saved_count']} client records to database")

        # Also load into data service for compatibility
        data_service.load_from_dataframe(df)

        return {
            "message": "CSV uploaded and saved to database successfully",
            "original_filename": file.filename,
            "batch_id": db_result["batch_id"],
            "total_clients": len(clients_data),
            "saved_to_database": db_result["saved_count"],
            "columns": list(df.columns),
            "clients_data": clean_for_json(clients_data),
            "sample_client": clean_for_json(clients_data[0] if clients_data else {}),
            "database_errors": db_result.get("errors", [])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/entities")
async def frontend_get_entities():
    """
    Get all entities from database in format expected by frontend
    """
    try:
        # Get entities from database
        clients_data = database_service.get_all_clients()
        
        # Clean the data for JSON response
        cleaned_data = clean_for_json(clients_data)

        return {
            "message": "Entities retrieved from database successfully",
            "total_clients": len(cleaned_data),
            "clients_data": cleaned_data
        }

    except Exception as e:
        logger.error(f"Error getting entities from database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get entities: {str(e)}")

@router.post("/analyze-batch")
async def frontend_analyze_batch(clients_data: List[Dict[str, Any]]):
    """
    Analyze batch of clients for frontend
    Returns results in format expected by frontend
    """
    try:
        if not clients_data:
            raise HTTPException(status_code=400, detail="No client data provided")

        results = []
        
        # Mock analysis for each client (replace with real logic later)
        for i, client in enumerate(clients_data):
            # Generate mock results
            risk_level = "Low" if i % 3 == 0 else "Amber" if i % 3 == 1 else "Red"
            approval_pct = 85 if risk_level == "Low" else 65 if risk_level == "Amber" else 25
            
            result = {
                "applicant_id": f"CUS-{10000 + i}",
                "entity_name": client.get("entity_name", f"Client-{i+1}"),
                "final_evaluation": risk_level,
                "approval_prediction_pct": approval_pct,
                "status": "Accepted" if risk_level == "Low" else "Under Review" if risk_level == "Amber" else "Rejected",
                "color": "green" if risk_level == "Low" else "yellow" if risk_level == "Amber" else "red",
                "date": pd.Timestamp.now().strftime("%b %d, %Y"),
                "factors": [
                    {
                        "factor": "debt_to_equity",
                        "evaluation": risk_level,
                        "value": client.get("debt_to_equity", 1.0)
                    }
                ],
                "summary": f"Mock analysis for {client.get('entity_name', 'client')} - {risk_level} risk profile"
            }
            results.append(result)

        return {
            "message": f"Batch analysis complete: {len(results)} applications processed",
            "total_processed": len(results),
            "results": clean_for_json(results)
        }

    except Exception as e:
        logger.error(f"Batch analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@router.get("/database-stats")
async def frontend_database_stats():
    """
    Get database statistics for frontend
    """
    try:
        stats = database_service.get_database_stats()
        return {
            "message": "Database statistics retrieved successfully",
            "stats": clean_for_json(stats)
        }
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get database stats: {str(e)}")

@router.post("/upload-csv-to-queue")
async def frontend_upload_csv_to_queue(file: UploadFile = File(...)):
    """
    Upload CSV to processing queue with 'unprocessed' status
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")

        # Read file content
        content = await file.read()
        
        # Parse CSV
        try:
            df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')
        except Exception as parse_error:
            try:
                df = pd.read_csv(io.BytesIO(content), encoding='latin-1')
            except Exception as encoding_error:
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not parse CSV file: {encoding_error}"
                )

        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")

        logger.info(f"CSV loaded for processing queue: {df.shape[0]} rows, {df.shape[1]} columns")

        # Convert DataFrame to list of dictionaries
        clients_data = []
        for _, row in df.iterrows():
            client = {}
            for col in df.columns:
                value = row[col]
                # Handle NaN values
                if pd.isna(value):
                    client[col] = None
                elif isinstance(value, (int, float)):
                    client[col] = float(value) if not pd.isna(value) else None
                else:
                    client[col] = str(value)
            clients_data.append(client)

        # Save to processing queue
        db_result = database_service.save_csv_to_processing_queue(clients_data, file.filename)
        
        if not db_result["success"]:
            raise HTTPException(status_code=500, detail="Failed to save data to processing queue")

        logger.info(f"Saved {db_result['saved_count']} client records to processing queue")

        return {
            "message": "CSV uploaded to processing queue successfully",
            "original_filename": file.filename,
            "batch_id": db_result["batch_id"],
            "total_clients": len(clients_data),
            "saved_to_queue": db_result["saved_count"],
            "columns": list(df.columns),
            "queue_errors": db_result.get("errors", [])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload to queue error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload to queue failed: {str(e)}")

@router.get("/processing-queue")
async def frontend_get_processing_queue(status: str = None, limit: int = None):
    """
    Get items from processing queue, optionally filtered by status
    """
    try:
        items = database_service.get_processing_queue_items(status=status, limit=limit)
        cleaned_data = clean_for_json(items)

        return {
            "message": f"Processing queue items retrieved successfully",
            "total_items": len(cleaned_data),
            "filter_status": status,
            "items": cleaned_data
        }

    except Exception as e:
        logger.error(f"Error getting processing queue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get processing queue: {str(e)}")

@router.put("/processing-queue/{item_id}/status")
async def frontend_update_processing_status(item_id: int, new_status: str, notes: str = None):
    """
    Update the processing status of a queue item
    """
    try:
        success = database_service.update_processing_status(item_id, new_status, notes)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Processing queue item {item_id} not found")

        return {
            "message": f"Processing status updated successfully",
            "item_id": item_id,
            "new_status": new_status,
            "notes": notes
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating processing status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update processing status: {str(e)}")

@router.get("/processing-queue-stats")
async def frontend_get_processing_queue_stats():
    """
    Get processing queue statistics
    """
    try:
        stats = database_service.get_processing_queue_stats()
        return {
            "message": "Processing queue statistics retrieved successfully",
            "stats": clean_for_json(stats)
        }
    except Exception as e:
        logger.error(f"Error getting processing queue stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get processing queue stats: {str(e)}")

@router.delete("/clear-database")
async def frontend_clear_database():
    """
    Clear all data from database (for development/testing)
    """
    try:
        result = database_service.clear_all_data()
        return {
            "message": "Database cleared successfully",
            "deleted_count": result["deleted_count"]
        }
    except Exception as e:
        logger.error(f"Error clearing database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear database: {str(e)}")

@router.delete("/clear-processing-queue")
async def frontend_clear_processing_queue():
    """
    Clear all items from processing queue (for development/testing)
    """
    try:
        result = database_service.clear_processing_queue()
        return {
            "message": "Processing queue cleared successfully",
            "deleted_count": result["deleted_count"]
        }
    except Exception as e:
        logger.error(f"Error clearing processing queue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear processing queue: {str(e)}")

@router.get("/health")
async def frontend_health():
    """
    Health check for frontend connectivity
    """
    try:
        db_stats = database_service.get_database_stats()
        queue_stats = database_service.get_processing_queue_stats()
        
        dashboard_stats = database_service.get_dashboard_stats()
        
        return {
            "status": "healthy",
            "service": "frontend_api",
            "database_connected": True,
            "total_clients_in_db": db_stats["total_clients"],
            "processing_queue_items": queue_stats["total_items"],
            "unprocessed_items": queue_stats["unprocessed_count"],
            "dashboard_initialized": dashboard_stats is not None,
            "total_applications_processed": dashboard_stats.get("total_applications_processed", 0),
            "data_service_loaded": data_service.get_data_status()["has_data"],
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as db_error:
        return {
            "status": "degraded",
            "service": "frontend_api",
            "database_connected": False,
            "database_error": str(db_error),
            "data_service_loaded": data_service.get_data_status()["has_data"],
            "timestamp": pd.Timestamp.now().isoformat()
        }

@router.get("/dashboard-stats")
async def get_dashboard_statistics():
    """
    Get dashboard statistics for the executive dashboard
    """
    try:
        stats = database_service.get_dashboard_stats()
        clean_stats = clean_for_json(stats)
        
        return {
            "success": True,
            "dashboard_stats": clean_stats,
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting dashboard stats: {str(e)}")

@router.put("/dashboard-stats")
async def update_dashboard_statistics(stats_data: dict):
    """
    Update dashboard statistics
    """
    try:
        updated_stats = database_service.update_dashboard_stats(stats_data)
        clean_stats = clean_for_json(updated_stats)
        
        return {
            "success": True,
            "message": "Dashboard statistics updated successfully",
            "updated_stats": clean_stats,
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error updating dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating dashboard stats: {str(e)}")

@router.post("/dashboard-stats/refresh")
async def refresh_dashboard_statistics():
    """
    Refresh dashboard statistics based on actual client data
    """
    try:
        refreshed_stats = database_service.refresh_dashboard_stats_from_data()
        clean_stats = clean_for_json(refreshed_stats)
        
        return {
            "success": True,
            "message": "Dashboard statistics refreshed from actual data",
            "refreshed_stats": clean_stats,
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error refreshing dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error refreshing dashboard stats: {str(e)}")

@router.post("/dashboard-stats/initialize")
async def initialize_dashboard_statistics():
    """
    Initialize dashboard statistics with default sample data
    """
    try:
        default_stats = database_service.create_default_dashboard_stats()
        clean_stats = clean_for_json(default_stats)
        
        return {
            "success": True,
            "message": "Dashboard statistics initialized with sample data",
            "initialized_stats": clean_stats,
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error initializing dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error initializing dashboard stats: {str(e)}")