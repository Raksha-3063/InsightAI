import os
import pandas as pd
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, status, Query
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from app.database.connection import db_helper
from app.auth.routes import get_current_user
from app.models.user import User
from app.routes.dataset import load_dataset_df
from app.ml.persistence.service import save_model_pipeline, load_model_pipeline, delete_model_pipeline
from app.ml.forecasting.detector import detect_time_series
from app.ml.forecasting.engine import train_forecasting_model
from app.ml.explainability.service import get_shap_explanations, get_lime_explanation
from app.ml.explainability.recommendations import generate_business_recommendations
from app.config import settings
from app.tasks.jobs import train_forecast_task, explainability_task

router = APIRouter()

class ForecastTrainRequest(BaseModel):
    datasetId: str
    dateColumn: str
    targetColumn: str
    algorithm: str
    horizon: int = 30
    confidenceLevel: float = 0.95
    seasonalPeriod: int = 7
    trainRatio: float = 0.8

class ForecastResponse(BaseModel):
    id: str = Field(..., alias="_id")
    projectId: str
    datasetId: str
    dateColumn: str
    targetColumn: str
    algorithm: str
    horizon: int
    confidenceLevel: float
    seasonalPeriod: int
    metrics: Dict[str, Any]
    createdDate: datetime
    status: Optional[str] = "completed"

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }

@router.get("/{projectId}/forecast/detect")
async def detect_forecast_feasibility(
    projectId: str,
    datasetId: str = Query(...),
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId) or not ObjectId.is_valid(datasetId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")
        
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    dataset_doc = await db_helper.db.datasets.find_one({"_id": ObjectId(datasetId), "projectId": projectId})
    if not dataset_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
        
    df = load_dataset_df(dataset_doc["filePath"])
    return detect_time_series(df)

@router.post("/{projectId}/forecast/train", status_code=status.HTTP_201_CREATED)
async def train_forecast(
    projectId: str,
    request: ForecastTrainRequest,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId) or not ObjectId.is_valid(request.datasetId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")
        
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    dataset_doc = await db_helper.db.datasets.find_one({"_id": ObjectId(request.datasetId), "projectId": projectId})
    if not dataset_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
        
    df = load_dataset_df(dataset_doc["filePath"])
    
    # Run TS detection to infer freq
    detection = detect_time_series(df)
    freq = detection.get("frequency") or "D"
    
    model_oid = ObjectId()
    model_id = str(model_oid)

    # 5. Branch based on Celery enabled status
    if settings.CELERY_ENABLED:
        forecast_doc = {
            "_id": model_oid,
            "projectId": projectId,
            "datasetId": request.datasetId,
            "dateColumn": request.dateColumn,
            "targetColumn": request.targetColumn,
            "algorithm": request.algorithm,
            "horizon": request.horizon,
            "confidenceLevel": request.confidenceLevel,
            "seasonalPeriod": request.seasonalPeriod,
            "metrics": {},
            "filePath": "",
            "createdDate": datetime.now(timezone.utc),
            "status": "pending"
        }
        await db_helper.db.forecasts.insert_one(forecast_doc)
        
        # Dispatch Celery background task
        train_forecast_task.delay(
            forecast_id=model_id,
            project_id=projectId,
            dataset_id=request.datasetId,
            file_path=dataset_doc["filePath"],
            target_column=request.targetColumn,
            date_column=request.dateColumn,
            algorithm=request.algorithm.lower(),
            horizon=request.horizon,
            seasonal_period=request.seasonalPeriod,
            confidence_level=request.confidenceLevel,
            train_ratio=request.trainRatio
        )
        
        forecast_doc["_id"] = model_id
        return ForecastResponse(**forecast_doc)

    # Synchronous Fallback Execution
    try:
        model, metrics, visuals = train_forecasting_model(
            df=df,
            date_col=request.dateColumn,
            target_col=request.targetColumn,
            algorithm=request.algorithm.lower(),
            horizon=request.horizon,
            confidence_level=request.confidenceLevel,
            seasonal_period=request.seasonalPeriod,
            train_ratio=request.trainRatio,
            freq=freq
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Forecasting model training failed: {str(e)}"
        )
        
    file_path = save_model_pipeline(f"forecast_{model_id}", model)
    
    forecast_doc = {
        "_id": model_oid,
        "projectId": projectId,
        "datasetId": request.datasetId,
        "dateColumn": request.dateColumn,
        "targetColumn": request.targetColumn,
        "algorithm": request.algorithm,
        "horizon": request.horizon,
        "confidenceLevel": request.confidenceLevel,
        "seasonalPeriod": request.seasonalPeriod,
        "metrics": metrics,
        "filePath": file_path,
        "createdDate": datetime.now(timezone.utc),
        "status": "completed"
    }
    await db_helper.db.forecasts.insert_one(forecast_doc)
    
    visuals_doc = {
        "forecastId": model_id,
        "visuals": visuals
    }
    await db_helper.db.forecast_visuals.insert_one(visuals_doc)
    
    forecast_doc["_id"] = model_id
    return ForecastResponse(**forecast_doc)

@router.get("/{projectId}/forecast/models", response_model=List[ForecastResponse])
async def list_forecasts(projectId: str, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(projectId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID")
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    cursor = db_helper.db.forecasts.find({"projectId": projectId})
    forecasts = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        forecasts.append(ForecastResponse(**doc))
    return forecasts

@router.get("/{projectId}/forecast/models/{modelId}", response_model=ForecastResponse)
async def get_forecast(
    projectId: str,
    modelId: str,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId) or not ObjectId.is_valid(modelId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID formats")
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    doc = await db_helper.db.forecasts.find_one({"_id": ObjectId(modelId), "projectId": projectId})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forecasting model not found")
        
    doc["_id"] = str(doc["_id"])
    return ForecastResponse(**doc)

@router.get("/{projectId}/forecast/models/{modelId}/visuals")
async def get_forecast_visuals(
    projectId: str,
    modelId: str,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId) or not ObjectId.is_valid(modelId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID formats")
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    doc = await db_helper.db.forecast_visuals.find_one({"forecastId": modelId})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visual coordinates not found")
        
    return doc["visuals"]

@router.get("/{projectId}/models/{mlModelId}/explanations")
async def get_ml_model_explanations(
    projectId: str,
    mlModelId: str,
    rowIndex: int = Query(0, alias="rowIndex"),
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId) or not ObjectId.is_valid(mlModelId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID formats")
        
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    # Get ML Model record
    model_doc = await db_helper.db.models.find_one({"_id": ObjectId(mlModelId), "projectId": projectId})
    if not model_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine Learning model not found")
        
    if settings.CELERY_ENABLED:
        job_oid = ObjectId()
        job_id = str(job_oid)
        job_doc = {
            "_id": job_oid,
            "projectId": projectId,
            "jobType": "explainability",
            "status": "pending",
            "createdDate": datetime.now(timezone.utc)
        }
        await db_helper.db.background_jobs.insert_one(job_doc)
        
        explainability_task.delay(
            job_id=job_id,
            project_id=projectId,
            model_id=mlModelId,
            row_index=rowIndex
        )
        return {
            "jobId": job_id,
            "status": "pending"
        }

    # Load dataset
    dataset_doc = await db_helper.db.datasets.find_one({"_id": ObjectId(model_doc["datasetId"]), "projectId": projectId})
    if not dataset_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset associated with model not found")
        
    df = load_dataset_df(dataset_doc["filePath"])
    X_train = df[model_doc["features"]]
    
    # Load serialized model pipeline
    try:
        save_data = load_model_pipeline(model_doc["filePath"])
        pipeline = save_data["pipeline"]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to load pipeline file: {str(e)}")
        
    # Resolve target instance for LIME explanation
    if rowIndex < 0 or rowIndex >= len(df):
        rowIndex = 0
    instance = X_train.iloc[rowIndex]
    
    # Compute explanations
    shap_data = get_shap_explanations(pipeline, X_train)
    lime_data = get_lime_explanation(pipeline, X_train, instance)
    
    return {
        "shap": shap_data,
        "lime": lime_data,
        "featuresUsed": model_doc["features"],
        "targetInstance": instance.to_dict()
    }

@router.get("/{projectId}/models/{mlModelId}/recommendations")
async def get_ml_model_recommendations(
    projectId: str,
    mlModelId: str,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId) or not ObjectId.is_valid(mlModelId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID formats")
        
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    # Get ML Model record
    model_doc = await db_helper.db.models.find_one({"_id": ObjectId(mlModelId), "projectId": projectId})
    if not model_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine Learning model not found")
        
    # Load dataset
    dataset_doc = await db_helper.db.datasets.find_one({"_id": ObjectId(model_doc["datasetId"]), "projectId": projectId})
    if not dataset_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset associated with model not found")
        
    df = load_dataset_df(dataset_doc["filePath"])
    
    return generate_business_recommendations(
        df=df,
        features=model_doc["features"],
        feature_importances=model_doc["featureImportance"]
    )
