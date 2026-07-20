import os
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Request
from fastapi.concurrency import run_in_threadpool
from bson import ObjectId
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.database.connection import db_helper
from app.schemas.dataset import DatasetResponse
from app.auth.routes import get_current_user
from app.models.user import User
from app.services.parser import parse_file_metadata
from app.config import settings
from app.ml.profiling.service import profile_dataframe
from app.ml.preprocessing.service import apply_cleaning_operation
from app.ml.statistics.service import calculate_numerical_statistics, calculate_categorical_statistics, calculate_correlations
from app.ml.visualization.service import (
    generate_histogram_data, generate_box_plot_data, generate_scatter_data,
    generate_pie_chart_data, generate_bar_chart_data, generate_line_chart_data
)
from app.ml.insights.service import calculate_dataset_health, generate_dataset_insights

router = APIRouter()

@router.post("/{projectId}/datasets/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    projectId: str, 
    request: Request,
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_user)
):
    # Validate project ID format
    if not ObjectId.is_valid(projectId):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )

    # Check project exists and belongs to current user
    project = await db_helper.db.projects.find_one({
        "_id": ObjectId(projectId),
        "userId": current_user.id
    })
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Validate file extension
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in [".csv", ".xlsx", ".xls"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file extension. Only CSV and Excel (.xlsx, .xls) are supported."
        )

    # Validate MIME type
    content_type = file.content_type
    allowed_types = [
        "text/csv",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "application/octet-stream" # Fallback for some OS/browsers
    ]
    if content_type not in allowed_types and file_ext not in [".csv", ".xlsx", ".xls"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported MIME type. Only CSV and Excel files are supported."
        )

    # Read and check file size (max 50MB)
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            length = int(content_length)
            if length > 50 * 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="File size exceeds the 50MB limit."
                )
        except ValueError:
            pass

    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read file: {str(e)}"
        )

    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 50MB limit."
        )

    # Create safe local storage path
    safe_filename = f"{projectId}_{int(datetime.now(timezone.utc).timestamp())}_{filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    # Save file to disk
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Parse metadata inside threadpool to prevent blocking the event loop
    try:
        metadata = await run_in_threadpool(parse_file_metadata, file_path, file_ext)
    except Exception as e:
        # Clean up file on failure
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse dataset file: {str(e)}"
        )

    # Build dataset document
    dataset_dict = {
        "projectId": projectId,
        "fileName": filename,
        "filePath": file_path,
        "rows": metadata["rows"],
        "columns": metadata["columns"],
        "missingValues": metadata["missingValues"],
        "duplicateRows": metadata["duplicateRows"],
        "size": metadata["size"],
        "columnTypes": metadata["columnTypes"],
        "numericalColumns": metadata["numericalColumns"],
        "categoricalColumns": metadata["categoricalColumns"],
        "dateColumns": metadata["dateColumns"],
        "uploadDate": datetime.now(timezone.utc),
        "cleaningHistory": []
    }

    # Save to MongoDB
    result = await db_helper.db.datasets.insert_one(dataset_dict)
    dataset_dict["_id"] = str(result.inserted_id)

    return DatasetResponse(**dataset_dict)

@router.get("/{projectId}/datasets", response_model=DatasetResponse)
async def get_project_dataset(projectId: str, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(projectId):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    # Check project exists and belongs to current user
    project = await db_helper.db.projects.find_one({
        "_id": ObjectId(projectId),
        "userId": current_user.id
    })
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Fetch the latest dataset associated with this project
    dataset_doc = await db_helper.db.datasets.find_one(
        {"projectId": projectId},
        sort=[("uploadDate", -1)]
    )
    if not dataset_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No dataset found for this project"
        )
        
    dataset_doc["_id"] = str(dataset_doc["_id"])
    return DatasetResponse(**dataset_doc)

@router.delete("/{projectId}/datasets", status_code=status.HTTP_200_OK)
async def delete_dataset(projectId: str, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(projectId):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    # Check project exists and belongs to current user
    project = await db_helper.db.projects.find_one({
        "_id": ObjectId(projectId),
        "userId": current_user.id
    })
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
        
    # Find all datasets associated with this project to delete files
    cursor = db_helper.db.datasets.find({"projectId": projectId})
    async for dataset_doc in cursor:
        file_path = dataset_doc.get("filePath")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete file {file_path}: {e}")
        # Also clean up raw file copy if present
        raw_path = dataset_doc.get("rawFilePath")
        if raw_path and os.path.exists(raw_path):
            try:
                os.remove(raw_path)
            except Exception as e:
                print(f"Failed to delete raw file {raw_path}: {e}")
                
    result = await db_helper.db.datasets.delete_many({"projectId": projectId})
    return {"message": "Dataset deleted successfully", "count": result.deleted_count}

class CleanRequest(BaseModel):
    opType: str
    params: Dict[str, Any]

import functools

@functools.lru_cache(maxsize=8)
def _load_cached_df(file_path: str, mtime: float) -> pd.DataFrame:
    ext_path = file_path
    if ext_path.endswith("_raw"):
        ext_path = ext_path[:-4]
    file_ext = os.path.splitext(ext_path)[1].lower()
    if file_ext == ".csv":
        return pd.read_csv(file_path)
    elif file_ext in [".xlsx", ".xls"]:
        return pd.read_excel(file_path, engine="openpyxl")
    raise ValueError("Unsupported file format")

def load_dataset_df(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset file not found: {file_path}"
        )
    mtime = os.path.getmtime(file_path)
    try:
        # Return a copy of the dataframe to prevent inline modification pollution
        return _load_cached_df(file_path, mtime).copy()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to load dataset: {str(e)}"
        )


# Helper function to check project and get latest dataset
async def get_and_validate_dataset(projectId: str, userId: str) -> dict:
    if not ObjectId.is_valid(projectId):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    project = await db_helper.db.projects.find_one({
        "_id": ObjectId(projectId),
        "userId": userId
    })
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    dataset_doc = await db_helper.db.datasets.find_one(
        {"projectId": projectId},
        sort=[("uploadDate", -1)]
    )
    if not dataset_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No dataset found for this project"
        )
    return dataset_doc

@router.get("/{projectId}/datasets/profile")
async def get_profile(projectId: str, current_user: User = Depends(get_current_user)):
    dataset_doc = await get_and_validate_dataset(projectId, current_user.id)
    df = load_dataset_df(dataset_doc["filePath"])
    return profile_dataframe(df)

@router.post("/{projectId}/datasets/clean", response_model=DatasetResponse)
async def clean_dataset(projectId: str, request: CleanRequest, current_user: User = Depends(get_current_user)):
    dataset_doc = await get_and_validate_dataset(projectId, current_user.id)
    
    file_path = dataset_doc["filePath"]
    raw_path = dataset_doc.get("rawFilePath")
    
    # Save original copy if not already backed up
    if not raw_path:
        raw_path = f"{file_path}_raw"
        try:
            import shutil
            shutil.copyfile(file_path, raw_path)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create raw dataset backup: {str(e)}"
            )
            
    df = load_dataset_df(file_path)
    
    try:
        df_cleaned = apply_cleaning_operation(df, request.opType, request.params)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
        
    # Save clean df
    file_ext = os.path.splitext(file_path)[1].lower()
    try:
        if file_ext == ".csv":
            df_cleaned.to_csv(file_path, index=False)
        else:
            df_cleaned.to_excel(file_path, index=False, engine="openpyxl")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save cleaned dataset: {str(e)}"
        )
        
    # Re-profile
    profiling = profile_dataframe(df_cleaned)
    
    # Update MongoDB metadata
    history = dataset_doc.get("cleaningHistory", [])
    history.append({
        "opType": request.opType,
        "params": request.params,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    update_data = {
        "rows": profiling["rows"],
        "columns": profiling["columns"],
        "missingValues": profiling["missingValues"],
        "duplicateRows": profiling["duplicateRows"],
        "size": os.path.getsize(file_path),
        "columnTypes": profiling["columnTypes"],
        "numericalColumns": profiling["numericalColumns"],
        "categoricalColumns": profiling["categoricalColumns"],
        "dateColumns": profiling["dateColumns"],
        "rawFilePath": raw_path,
        "cleaningHistory": history
    }
    
    await db_helper.db.datasets.update_one(
        {"_id": ObjectId(dataset_doc["_id"])},
        {"$set": update_data}
    )
    
    dataset_doc.update(update_data)
    dataset_doc["_id"] = str(dataset_doc["_id"])
    return DatasetResponse(**dataset_doc)

@router.post("/{projectId}/datasets/revert", response_model=DatasetResponse)
async def revert_clean(projectId: str, current_user: User = Depends(get_current_user)):
    dataset_doc = await get_and_validate_dataset(projectId, current_user.id)
    history = dataset_doc.get("cleaningHistory", [])
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No cleaning history to revert."
        )
        
    raw_path = dataset_doc.get("rawFilePath")
    if not raw_path or not os.path.exists(raw_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Original raw dataset backup not found."
        )
        
    # Pop last operation
    history.pop()
    
    # Load original raw dataframe
    df = load_dataset_df(raw_path)
    
    # Re-apply all remaining operations
    for op in history:
        df = apply_cleaning_operation(df, op["opType"], op["params"])
        
    file_path = dataset_doc["filePath"]
    file_ext = os.path.splitext(file_path)[1].lower()
    try:
        if file_ext == ".csv":
            df.to_csv(file_path, index=False)
        else:
            df.to_excel(file_path, index=False, engine="openpyxl")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save reverted dataset: {str(e)}"
        )
        
    # Re-profile
    profiling = profile_dataframe(df)
    
    update_data = {
        "rows": profiling["rows"],
        "columns": profiling["columns"],
        "missingValues": profiling["missingValues"],
        "duplicateRows": profiling["duplicateRows"],
        "size": os.path.getsize(file_path),
        "columnTypes": profiling["columnTypes"],
        "numericalColumns": profiling["numericalColumns"],
        "categoricalColumns": profiling["categoricalColumns"],
        "dateColumns": profiling["dateColumns"],
        "cleaningHistory": history
    }
    
    await db_helper.db.datasets.update_one(
        {"_id": ObjectId(dataset_doc["_id"])},
        {"$set": update_data}
    )
    
    dataset_doc.update(update_data)
    dataset_doc["_id"] = str(dataset_doc["_id"])
    return DatasetResponse(**dataset_doc)

@router.get("/{projectId}/datasets/statistics")
async def get_statistics(projectId: str, current_user: User = Depends(get_current_user)):
    dataset_doc = await get_and_validate_dataset(projectId, current_user.id)
    df = load_dataset_df(dataset_doc["filePath"])
    
    numerical_stats = calculate_numerical_statistics(df, dataset_doc.get("numericalColumns", []))
    categorical_stats = calculate_categorical_statistics(df, dataset_doc.get("categoricalColumns", []))
    
    return {
        "numerical": numerical_stats,
        "categorical": categorical_stats
    }

@router.get("/{projectId}/datasets/correlations")
async def get_correlations(projectId: str, current_user: User = Depends(get_current_user)):
    dataset_doc = await get_and_validate_dataset(projectId, current_user.id)
    df = load_dataset_df(dataset_doc["filePath"])
    
    num_cols = dataset_doc.get("numericalColumns", [])
    return calculate_correlations(df, num_cols)

@router.get("/{projectId}/datasets/visualizations")
async def get_visualizations(
    projectId: str, 
    col: str, 
    col_y: Optional[str] = None, 
    chart_type: str = "histogram",
    current_user: User = Depends(get_current_user)
):
    dataset_doc = await get_and_validate_dataset(projectId, current_user.id)
    df = load_dataset_df(dataset_doc["filePath"])
    
    if col not in df.columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Column '{col}' not found in dataset."
        )
        
    if chart_type == "histogram":
        return generate_histogram_data(df, col)
    elif chart_type == "boxplot":
        return generate_box_plot_data(df, col)
    elif chart_type == "pie":
        return generate_pie_chart_data(df, col)
    elif chart_type == "bar":
        return generate_bar_chart_data(df, col)
    elif chart_type == "scatter":
        if not col_y:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scatter plot requires 'col_y' query parameter."
            )
        if col_y not in df.columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Column '{col_y}' not found in dataset."
            )
        return generate_scatter_data(df, col, col_y)
    elif chart_type == "line":
        if not col_y:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Line chart requires 'col_y' (numerical column) query parameter."
            )
        if col_y not in df.columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Column '{col_y}' not found in dataset."
            )
        return generate_line_chart_data(df, col, col_y)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported chart type: {chart_type}."
        )

@router.get("/{projectId}/datasets/health-score")
async def get_health_score(projectId: str, current_user: User = Depends(get_current_user)):
    dataset_doc = await get_and_validate_dataset(projectId, current_user.id)
    df = load_dataset_df(dataset_doc["filePath"])
    
    profiling = profile_dataframe(df)
    return calculate_dataset_health(df, profiling)

@router.get("/{projectId}/datasets/insights")
async def get_insights(projectId: str, current_user: User = Depends(get_current_user)):
    dataset_doc = await get_and_validate_dataset(projectId, current_user.id)
    df = load_dataset_df(dataset_doc["filePath"])
    
    profiling = profile_dataframe(df)
    numerical_stats = calculate_numerical_statistics(df, dataset_doc.get("numericalColumns", []))
    
    return generate_dataset_insights(df, profiling, numerical_stats)
