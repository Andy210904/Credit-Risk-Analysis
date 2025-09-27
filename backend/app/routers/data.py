from fastapi import APIRouter, HTTPException, Query, Body, UploadFile, File, Request
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from app.models.data import (
    CreditEntity, CreditEntitiesList, RiskBucket, Sector, 
    OwnershipType, AuditorTier, IndustryCyclicality
)
from app.services.data_service import DataService
from pydantic import BaseModel
import logging
import httpx
import json
import pandas as pd
import numpy as np
import io
import os
import shutil
from datetime import datetime

router = APIRouter()
data_service = DataService()
logger = logging.getLogger(__name__)

def clean_for_json(obj):
    """
    Recursively clean data structure to make it JSON serializable
    by replacing NaN, inf, -inf with None
    """
    if isinstance(obj, dict):
        return {key: clean_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(item) for item in obj]
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif pd.isna(obj):
        return None
    else:
        return obj

@router.post("/analyze-csv")
async def analyze_csv_file(file: UploadFile = File(...)):
    """
    Analyze CSV file structure without processing it.
    This helps understand what columns and data types are in the file.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')
        
        # Get basic info about the CSV
        analysis = {
            "filename": file.filename,
            "shape": {"rows": len(df), "columns": len(df.columns)},
            "columns": list(df.columns),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "sample_data": df.head(3).to_dict('records'),
            "missing_values": df.isnull().sum().to_dict(),
            "required_columns": ['entity_id', 'entity_name', 'sector', 'country'],
            "missing_required_columns": [col for col in ['entity_id', 'entity_name', 'sector', 'country'] 
                                       if col not in df.columns]
        }
        
        return JSONResponse(content=clean_for_json(analysis))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing CSV: {str(e)}")

@router.post("/debug-request")
async def debug_request_endpoint(request: Request):
    """
    Debug endpoint to inspect the raw request details
    """
    try:
        headers = dict(request.headers)
        return {
            "message": "Request received",
            "method": request.method,
            "url": str(request.url),
            "headers": headers,
            "content_type": headers.get("content-type", "Not specified"),
            "content_length": headers.get("content-length", "Not specified")
        }
    except Exception as e:
        return {"error": f"Failed to inspect request: {str(e)}"}

@router.post("/upload-any-format")  
async def upload_any_format(
    request: Request,
    file: Optional[UploadFile] = File(None)
):
    """
    Accepts upload in any format and shows what was received
    """
    try:
        result = {
            "message": "Upload attempt received",
            "headers": dict(request.headers),
            "method": request.method,
            "content_type": request.headers.get("content-type"),
            "file_received": file is not None
        }
        
        if file:
            result["file_info"] = {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": getattr(file, 'size', 'unknown')
            }
        
        return result
        
    except Exception as e:
        return {"error": f"Error processing upload: {str(e)}"}

@router.post("/test-upload")
async def test_upload_endpoint(file: UploadFile = File(...)):
    """
    Simple test endpoint to debug file upload issues
    """
    try:
        return {
            "message": "File received successfully",
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file.size if hasattr(file, 'size') else "unknown"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in test upload: {str(e)}")

@router.post("/upload-csv-flexible")
async def upload_csv_flexible(file: Optional[UploadFile] = File(None)):
    """
    More flexible CSV upload endpoint with better error handling
    """
    try:
        if not file:
            raise HTTPException(
                status_code=400, 
                detail="No file provided. Make sure to include 'file' field in the form data."
            )
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="File has no filename")
            
        logger.info(f"Received file: {file.filename}, type: {file.content_type}")
        
        # More lenient file type checking
        if not (file.filename.lower().endswith('.csv') or file.content_type == 'text/csv'):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Expected CSV, got: {file.filename} ({file.content_type})"
            )
        
        # Try to read the file content
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Try to parse as CSV
        try:
            df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')
        except Exception as parse_error:
            raise HTTPException(
                status_code=400, 
                detail=f"Could not parse CSV file: {str(parse_error)}"
            )
        
        return {
            "message": "CSV uploaded successfully",
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in flexible upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/upload-csv-debug")
async def upload_csv_debug(request: Request):
    """
    Debug version of upload-csv that accepts any request and shows what's received
    """
    try:
        content_type = request.headers.get("content-type", "")
        logger.info(f"Debug upload received. Content-Type: {content_type}")
        
        # Try to get form data if it's multipart
        if "multipart/form-data" in content_type:
            try:
                form = await request.form()
                form_data = {}
                files_info = {}
                
                for key, value in form.items():
                    if hasattr(value, 'filename'):  # It's a file
                        files_info[key] = {
                            'filename': value.filename,
                            'content_type': getattr(value, 'content_type', 'unknown'),
                            'size': len(await value.read()) if hasattr(value, 'read') else 'unknown'
                        }
                    else:  # Regular form field
                        form_data[key] = str(value)
                
                return {
                    "message": "Multipart form data received",
                    "content_type": content_type,
                    "form_fields": form_data,
                    "files": files_info
                }
            except Exception as form_error:
                return {
                    "message": "Failed to parse multipart data",
                    "error": str(form_error),
                    "content_type": content_type
                }
        else:
            # Try to read as raw content
            try:
                body = await request.body()
                return {
                    "message": "Non-multipart request received",
                    "content_type": content_type,
                    "body_length": len(body),
                    "body_preview": body[:100].decode('utf-8', errors='ignore') if body else "Empty"
                }
            except Exception as body_error:
                return {
                    "message": "Failed to read body",
                    "error": str(body_error)
                }
                
    except Exception as e:
        return {
            "message": "Debug endpoint failed",
            "error": str(e)
        }

@router.post("/upload-csv")
async def upload_csv_file(file: UploadFile = File(...)):
    """
    Upload and process a CSV file containing credit entity data.
    Saves the file to the data folder and processes it.
    """
    # Add logging to see what we receive
    logger.info(f"Upload request received. File: {file.filename if file else 'None'}")
    
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
        
    if not file.filename:
        raise HTTPException(status_code=400, detail="File has no filename")
        
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    # Ensure data directory exists
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        logger.info(f"Created data directory: {data_dir}")

    # Generate filename with timestamp to avoid conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_filename = file.filename
    saved_filename = f"uploaded_{timestamp}_{original_filename}"
    file_path = os.path.join(data_dir, saved_filename)

    try:
        # Read the uploaded file content once
        content = await file.read()
        
        # Save the uploaded file to data folder EXACTLY as uploaded
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        logger.info(f"Saved uploaded file to: {file_path} (size: {len(content)} bytes)")

        # Now read the saved file with pandas (this preserves original formatting)
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_path, encoding='latin-1')
            except Exception as encoding_error:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Could not read CSV file. Encoding error: {encoding_error}"
                )
        except pd.errors.EmptyDataError:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        except pd.errors.ParserError as parse_error:
            raise HTTPException(
                status_code=400, 
                detail=f"CSV file format error: {parse_error}"
            )

        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file contains no data rows")

        logger.info(f"CSV loaded successfully. Shape: {df.shape}, Columns: {list(df.columns)}")

        # Check if this looks like our expected format
        expected_columns = [
            'entity_id', 'entity_name', 'sector', 'country', 'revenue_usd_m', 
            'ebitda_margin_pct', 'ebit_margin_pct', 'cash_usd_m', 'total_assets_usd_m'
        ]
        
        # Basic validation - just check for core required columns
        required_columns = ['entity_id', 'entity_name', 'sector', 'country']
        available_columns = [col.strip() for col in df.columns]
        
        missing_columns = []
        for req_col in required_columns:
            if req_col not in available_columns:
                missing_columns.append(req_col)
        
        if missing_columns:
            # Create detailed error message
            error_detail = {
                "error": "Missing required columns",
                "missing_columns": missing_columns,
                "available_columns": available_columns,
                "expected_format": "CSV should contain at least: " + ", ".join(required_columns)
            }
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {missing_columns}. Available: {available_columns}"
            )
        
        # Check if we have enough columns for full processing
        has_full_format = all(col in available_columns for col in expected_columns)
        logger.info(f"Full format check: {has_full_format} - Has {len(available_columns)} columns")
        
        # Load the data into the global data service
        try:
            success = data_service.load_from_dataframe(df)
            if not success:
                raise HTTPException(status_code=500, detail="Data service failed to process the DataFrame")
        except Exception as service_error:
            logger.error(f"Data service error: {service_error}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to process data: {service_error}"
            )

        # Handle NaN values for JSON serialization
        sample_entities = []
        if len(df) > 0:
            # Get sample data and clean for JSON serialization
            sample_data = df.head(3).to_dict('records')
            sample_entities = clean_for_json(sample_data)

        # Clean the entire response data
        response_data = {
            "message": "CSV file uploaded, saved, and processed successfully",
            "original_filename": original_filename,
            "saved_filename": saved_filename,
            "saved_path": file_path,
            "total_entities": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "sample_entities": sample_entities
        }

        return JSONResponse(
            status_code=200,
            content=clean_for_json(response_data)
        )
    except Exception as e:
        # Clean up the saved file if processing failed
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up failed upload file: {file_path}")
            except Exception as cleanup_error:
                logger.error(f"Failed to clean up file {file_path}: {cleanup_error}")
        
        logger.error(f"Failed to process CSV file '{file.filename}': {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the file: {e}")
    finally:
        # It's important to close the file stream.
        await file.close()

@router.get("/uploaded-files")
async def list_uploaded_files():
    """
    List all uploaded CSV files in the data folder
    """
    try:
        data_dir = "data"
        if not os.path.exists(data_dir):
            return {"files": [], "message": "No data directory found"}
        
        files = []
        for filename in os.listdir(data_dir):
            if filename.endswith('.csv'):
                file_path = os.path.join(data_dir, filename)
                file_stats = os.stat(file_path)
                
                files.append({
                    "filename": filename,
                    "file_path": file_path,
                    "size_bytes": file_stats.st_size,
                    "size_mb": round(file_stats.st_size / (1024 * 1024), 2),
                    "created_date": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                    "modified_date": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                    "is_uploaded": filename.startswith("uploaded_")
                })
        
        # Sort by creation date (newest first)
        files.sort(key=lambda x: x["created_date"], reverse=True)
        
        return {
            "files": files,
            "total_files": len(files),
            "data_directory": data_dir
        }
    except Exception as e:
        logger.error(f"Error listing uploaded files: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list uploaded files")


@router.get("/upload-status")
async def get_upload_status():
    """
    Check if CSV data has been uploaded and is available for analysis
    """
    try:
        status = data_service.get_data_status()
        return {
            "data_loaded": status["has_data"],
            "total_entities": status["total_entities"],
            "data_source": status["source"],
            "columns_available": status["columns"]
        }
    except Exception as e:
        logger.error(f"Error getting upload status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get upload status")

@router.post("/entities/{entity_name}/evaluate")
async def evaluate_entity_credit(entity_name: str):
    """
    Evaluate credit risk for a specific entity by name and send to ML service.
    This endpoint is triggered when clicking the 'Evaluate' button for a client.
    """
    try:
        # Find the entity by name (case-insensitive search)
        entities = data_service.get_all_entities()
        target_entity = None
        
        for entity in entities:
            if entity.entity_name.lower() == entity_name.lower():
                target_entity = entity
                break
        
        if not target_entity:
            # Try partial matching if exact match fails
            for entity in entities:
                if entity_name.lower() in entity.entity_name.lower():
                    target_entity = entity
                    break
        
        if not target_entity:
            raise HTTPException(
                status_code=404, 
                detail=f"Entity '{entity_name}' not found in uploaded data"
            )
        
        # Prepare entity data for ML service
        entity_data = {
            "entity_id": target_entity.entity_id,
            "entity_name": target_entity.entity_name,
            "sector": target_entity.sector,
            "country": target_entity.country,
            "financial_metrics": {
                "revenue_usd_m": target_entity.revenue_usd_m,
                "ebitda_margin_pct": target_entity.ebitda_margin_pct,
                "debt_to_equity": target_entity.debt_to_equity,
                "interest_coverage": target_entity.interest_coverage,
                "current_ratio": target_entity.current_ratio,
                "dscr": target_entity.dscr
            },
            "risk_metrics": {
                "pd_1y_pct": target_entity.pd_1y_pct,
                "lgd_pct": target_entity.lgd_pct,
                "risk_bucket": target_entity.risk_bucket,
                "implied_rating": target_entity.implied_rating
            },
            "governance_metrics": {
                "governance_score_0_100": target_entity.governance_score_0_100,
                "auditor_tier": target_entity.auditor_tier,
                "ownership_type": target_entity.ownership_type
            }
        }
        
        # Send to ML service for analysis
        ml_service_url = "http://localhost:8001/analyze-entity"
        
        try:
            async with httpx.AsyncClient() as client:
                ml_response = await client.post(
                    ml_service_url,
                    json={
                        "entity_data": entity_data,
                        "analysis_type": "comprehensive_credit_evaluation"
                    },
                    timeout=30.0
                )
                ml_response.raise_for_status()
                ml_result = ml_response.json()
        except httpx.RequestError:
            # If ML service is not available, return entity data with mock analysis
            ml_result = {
                "entity_id": target_entity.entity_id,
                "analysis_status": "ML service unavailable",
                "mock_analysis": {
                    "risk_assessment": "Medium Risk" if target_entity.risk_bucket.value == "Medium" else target_entity.risk_bucket.value,
                    "credit_score": round((100 - target_entity.pd_1y_pct * 10), 1),
                    "recommendation": f"Based on {target_entity.implied_rating} rating and {target_entity.debt_to_equity:.2f} debt-to-equity ratio"
                }
            }
        
        return {
            "entity_name": entity_name,
            "entity_data": clean_for_json(entity_data),
            "ml_analysis": clean_for_json(ml_result),
            "evaluation_timestamp": pd.Timestamp.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating entity '{entity_name}': {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to evaluate entity: {str(e)}"
        )

@router.get("/clients")
async def get_client_list():
    """
    Get list of all clients/entities for the evaluation dashboard.
    Returns simplified entity info suitable for the client list UI.
    """
    try:
        entities = data_service.get_all_entities()
        
        clients = []
        for entity in entities:
            client_info = {
                "entity_id": entity.entity_id,
                "client_name": entity.entity_name,
                "sector": entity.sector,
                "country": entity.country,
                "risk_bucket": entity.risk_bucket,
                "implied_rating": entity.implied_rating,
                "revenue_usd_m": entity.revenue_usd_m
            }
            clients.append(client_info)
        
        # Sort by entity name for consistent display
        clients.sort(key=lambda x: x["client_name"])
        
        return {
            "total_clients": len(clients),
            "clients": clean_for_json(clients)
        }
        
    except Exception as e:
        logger.error(f"Error getting client list: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get client list")

@router.delete("/clear-data")
async def clear_uploaded_data():
    """
    Clear all uploaded CSV data from memory
    """
    try:
        data_service.clear_data()
        return {"message": "All uploaded data has been cleared"}
    except Exception as e:
        logger.error(f"Error clearing data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear data")

@router.get("/entities", response_model=CreditEntitiesList)
async def get_all_entities():
    """
    Get all credit entities from uploaded CSV file.
    Note: CSV file must be uploaded first using the /upload-csv endpoint.
    """
    try:
        entities = data_service.get_all_entities()
        return CreditEntitiesList(
            total_count=len(entities),
            entities=entities
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching entities: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch entities")

@router.get("/entities/top-revenue", response_model=List[CreditEntity])
async def get_top_entities_by_revenue(limit: int = Query(10, description="Number of top entities to return")):
    """
    Get top entities by revenue
    """
    try:
        entities = data_service.get_top_entities_by_revenue(limit)
        return entities
    except Exception as e:
        logger.error(f"Error fetching top entities by revenue: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch top entities by revenue")

@router.get("/entities/risk/{risk_bucket}", response_model=List[CreditEntity])
async def get_entities_by_risk(risk_bucket: RiskBucket):
    """
    Get entities filtered by risk bucket
    """
    try:
        entities = data_service.get_entities_by_risk_bucket(risk_bucket)
        return entities
    except Exception as e:
        logger.error(f"Error fetching entities by risk {risk_bucket}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch entities by risk bucket")

@router.get("/entities/sector/{sector}", response_model=List[CreditEntity])
async def get_entities_by_sector(sector: Sector):
    """
    Get entities filtered by sector
    """
    try:
        entities = data_service.get_entities_by_sector(sector)
        return entities
    except Exception as e:
        logger.error(f"Error fetching entities by sector {sector}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch entities by sector")

@router.get("/entities/country/{country}", response_model=List[CreditEntity])
async def get_entities_by_country(country: str):
    """
    Get entities filtered by country
    """
    try:
        entities = data_service.get_entities_by_country(country)
        return entities
    except Exception as e:
        logger.error(f"Error fetching entities by country {country}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch entities by country")

@router.get("/entities/{entity_id}", response_model=CreditEntity)
async def get_entity_by_id(entity_id: str):
    """
    Get a specific credit entity by ID
    """
    try:
        entity = data_service.get_entity_by_id(entity_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        return entity
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching entity {entity_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch entity")

@router.get("/statistics")
async def get_data_statistics():
    """
    Get statistics about credit entities data
    """
    try:
        stats = data_service.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

@router.get("/search", response_model=List[CreditEntity])
async def search_entities(
    min_revenue: Optional[float] = Query(None, description="Minimum revenue filter (USD millions)"),
    max_revenue: Optional[float] = Query(None, description="Maximum revenue filter (USD millions)"),
    min_pd: Optional[float] = Query(None, description="Minimum PD (1y) filter"),
    max_pd: Optional[float] = Query(None, description="Maximum PD (1y) filter"),
    risk_bucket: Optional[RiskBucket] = Query(None, description="Risk bucket filter"),
    sector: Optional[Sector] = Query(None, description="Sector filter"),
    country: Optional[str] = Query(None, description="Country filter"),
    ownership_type: Optional[OwnershipType] = Query(None, description="Ownership type filter")
):
    """
    Search entities with multiple filters
    """
    try:
        entities = data_service.search_entities(
            min_revenue=min_revenue,
            max_revenue=max_revenue,
            min_pd=min_pd,
            max_pd=max_pd,
            risk_bucket=risk_bucket,
            sector=sector,
            country=country,
            ownership_type=ownership_type
        )
        return entities
    except Exception as e:
        logger.error(f"Error searching entities: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search entities")


# Pydantic models for ML service requests
