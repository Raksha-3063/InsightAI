import os
import shutil
import tempfile
import time
import pandas as pd
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.responses import FileResponse
from bson import ObjectId
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from app.database.connection import db_helper
from app.schemas.model import TrainRequest, PredictRequest, ModelResponse
from app.auth.routes import get_current_user
from app.models.user import User
from app.routes.dataset import load_dataset_df
from app.ml.training.regression import train_regression_model
from app.ml.training.classification import train_classification_model
from app.ml.training.clustering import train_clustering_model
from app.ml.persistence.service import save_model_pipeline, load_model_pipeline, delete_model_pipeline
from app.ml.prediction.service import predict_manual, predict_batch
from app.ml.comparison.service import compare_models

from app.config import settings
from app.tasks.jobs import train_ml_model_task, batch_prediction_task

router = APIRouter()

@router.post("/{projectId}/models/train", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def train_model(
    projectId: str,
    request: TrainRequest,
    current_user: User = Depends(get_current_user)
):
    # 1. Validate project ownership
    if not ObjectId.is_valid(projectId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format")
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    # 2. Fetch dataset record
    if not ObjectId.is_valid(request.datasetId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid dataset ID format")
    dataset_doc = await db_helper.db.datasets.find_one({"_id": ObjectId(request.datasetId), "projectId": projectId})
    if not dataset_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
        
    # 3. Load dataframe
    df = load_dataset_df(dataset_doc["filePath"])
    
    # 4. Classify task type
    algorithm = request.algorithm.lower()
    if algorithm in ["kmeans", "dbscan", "hierarchical"]:
        task_type = "clustering"
    else:
        if not request.targetColumn:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="targetColumn is required for supervised learning."
            )
        if request.targetColumn not in df.columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Target column '{request.targetColumn}' not found in dataset."
            )
        # Determine classification vs regression
        if request.targetColumn in dataset_doc.get("numericalColumns", []):
            task_type = "regression"
        else:
            task_type = "classification"
            
    # Auto-assign model name
    timestamp = datetime.now(timezone.utc).strftime("%M%S")
    model_name = f"{algorithm}_{timestamp}"
    
    # Generate model ID beforehand for joblib filename
    model_oid = ObjectId()
    model_id = str(model_oid)
    
    # Fetch column details from dataset record
    num_cols = dataset_doc.get("numericalColumns", [])
    cat_cols = dataset_doc.get("categoricalColumns", [])
    
    # 5. Branch based on Celery enabled status
    if settings.CELERY_ENABLED:
        model_dict = {
            "_id": model_oid,
            "projectId": projectId,
            "datasetId": request.datasetId,
            "modelName": model_name,
            "algorithm": algorithm,
            "taskType": task_type,
            "targetColumn": request.targetColumn,
            "features": request.features,
            "hyperparameters": request.hyperparameters,
            "metrics": {},
            "filePath": "",
            "trainingTime": 0.0,
            "featureImportance": [],
            "createdDate": datetime.now(timezone.utc),
            "status": "pending"
        }
        await db_helper.db.models.insert_one(model_dict)
        
        # Dispatch to worker
        train_ml_model_task.delay(
            model_id=model_id,
            project_id=projectId,
            dataset_id=request.datasetId,
            file_path=dataset_doc["filePath"],
            algorithm=algorithm,
            features=request.features,
            target_column=request.targetColumn,
            hyperparameters=request.hyperparameters,
            split_ratio=request.splitRatio,
            random_state=request.randomState,
            stratified=request.stratified,
            num_cols=num_cols,
            cat_cols=cat_cols,
            task_type=task_type
        )
        
        model_dict["_id"] = model_id
        return ModelResponse(**model_dict)

    # Synchronous Fallback Execution
    try:
        if task_type == "regression":
            pipeline, metrics, visuals, importance, train_time = train_regression_model(
                df, request.features, request.targetColumn, algorithm, request.hyperparameters,
                request.splitRatio, request.randomState, num_cols, cat_cols
            )
            target_encoder = None
            
        elif task_type == "classification":
            pipeline, target_encoder, metrics, visuals, importance, train_time = train_classification_model(
                df, request.features, request.targetColumn, algorithm, request.hyperparameters,
                request.splitRatio, request.randomState, request.stratified, num_cols, cat_cols
            )
            
        else:
            pipeline, metrics, visuals, train_time = train_clustering_model(
                df, request.features, algorithm, request.hyperparameters,
                request.randomState, num_cols, cat_cols
            )
            target_encoder = None
            importance = []
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Model training failed: {str(e)}"
        )
        
    save_data = {
        "pipeline": pipeline,
        "target_encoder": target_encoder
    }
    file_path = save_model_pipeline(model_id, save_data)
    
    model_dict = {
        "_id": model_oid,
        "projectId": projectId,
        "datasetId": request.datasetId,
        "modelName": model_name,
        "algorithm": algorithm,
        "taskType": task_type,
        "targetColumn": request.targetColumn,
        "features": request.features,
        "hyperparameters": request.hyperparameters,
        "metrics": metrics,
        "filePath": file_path,
        "trainingTime": train_time,
        "featureImportance": importance,
        "createdDate": datetime.now(timezone.utc),
        "status": "completed"
    }
    
    await db_helper.db.models.insert_one(model_dict)
    
    visuals_dict = {
        "modelId": model_id,
        "visuals": visuals
    }
    await db_helper.db.model_visuals.insert_one(visuals_dict)
    
    model_dict["_id"] = model_id
    return ModelResponse(**model_dict)

@router.get("/{projectId}/models", response_model=List[ModelResponse])
async def list_models(projectId: str, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(projectId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format")
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    cursor = db_helper.db.models.find({"projectId": projectId})
    models = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        models.append(ModelResponse(**doc))
    return models

@router.get("/{projectId}/models/compare")
async def compare_workspace_models(
    projectId: str,
    metric: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format")
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    cursor = db_helper.db.models.find({"projectId": projectId})
    models = []
    async for doc in cursor:
        models.append(doc)
        
    return compare_models(models, metric)

@router.get("/{projectId}/models/{modelId}", response_model=ModelResponse)
async def get_model(
    projectId: str,
    modelId: str,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId) or not ObjectId.is_valid(modelId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID formats")
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    model_doc = await db_helper.db.models.find_one({"_id": ObjectId(modelId), "projectId": projectId})
    if not model_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
        
    model_doc["_id"] = str(model_doc["_id"])
    return ModelResponse(**model_doc)

@router.get("/{projectId}/models/{modelId}/visuals")
async def get_model_visuals(
    projectId: str,
    modelId: str,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId) or not ObjectId.is_valid(modelId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID formats")
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    visuals_doc = await db_helper.db.model_visuals.find_one({"modelId": modelId})
    if not visuals_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visual coordinates not found")
        
    return visuals_doc["visuals"]

@router.delete("/{projectId}/models/{modelId}", status_code=status.HTTP_200_OK)
async def delete_model(
    projectId: str,
    modelId: str,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId) or not ObjectId.is_valid(modelId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID formats")
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    model_doc = await db_helper.db.models.find_one({"_id": ObjectId(modelId), "projectId": projectId})
    if not model_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
        
    # Delete model file from local storage
    try:
        delete_model_pipeline(model_doc["filePath"])
    except Exception:
        pass
        
    # Delete from MongoDB collections
    await db_helper.db.models.delete_one({"_id": ObjectId(modelId)})
    await db_helper.db.model_visuals.delete_one({"modelId": modelId})
    
    return {"message": "Model deleted successfully"}

@router.post("/{projectId}/models/{modelId}/predict")
async def run_predict_manual(
    projectId: str,
    modelId: str,
    request: PredictRequest,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId) or not ObjectId.is_valid(modelId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID formats")
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    model_doc = await db_helper.db.models.find_one({"_id": ObjectId(modelId), "projectId": projectId})
    if not model_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
        
    # Load serialized model & target encoder
    try:
        save_data = load_model_pipeline(model_doc["filePath"])
        pipeline = save_data["pipeline"]
        target_encoder = save_data["target_encoder"]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to load model file: {str(e)}")
        
    try:
        predictions = predict_manual(pipeline, model_doc["features"], request.data, target_encoder)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Prediction failed: {str(e)}")
        
    return {"predictions": predictions}

@router.post("/{projectId}/models/{modelId}/predict/file")
async def run_predict_file(
    projectId: str,
    modelId: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId) or not ObjectId.is_valid(modelId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID formats")
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    model_doc = await db_helper.db.models.find_one({"_id": ObjectId(modelId), "projectId": projectId})
    if not model_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
        
    # Validate extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".csv", ".xlsx", ".xls"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file format. Upload CSV or Excel.")
        
    # Save upload file to local location
    try:
        persistent_filename = f"batch_{modelId}_{int(time.time())}{file_ext}"
        persistent_file_path = os.path.join(settings.UPLOAD_DIR, persistent_filename)
        with open(persistent_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to store uploaded batch file: {str(e)}")
        
    if settings.CELERY_ENABLED:
        job_oid = ObjectId()
        job_id = str(job_oid)
        job_doc = {
            "_id": job_oid,
            "projectId": projectId,
            "jobType": "batch_prediction",
            "status": "pending",
            "createdDate": datetime.now(timezone.utc)
        }
        await db_helper.db.background_jobs.insert_one(job_doc)
        
        batch_prediction_task.delay(
            job_id=job_id,
            project_id=projectId,
            model_id=modelId,
            file_path=persistent_file_path
        )
        return {
            "jobId": job_id,
            "status": "pending"
        }

    # Synchronous Fallback Execution
    try:
        save_data = load_model_pipeline(model_doc["filePath"])
        pipeline = save_data["pipeline"]
        target_encoder = save_data["target_encoder"]
    except Exception as e:
        if os.path.exists(persistent_file_path):
            os.remove(persistent_file_path)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to load model file: {str(e)}")
        
    try:
        df_predicted, predicted_file_path = predict_batch(pipeline, model_doc["features"], persistent_file_path, target_encoder)
    except Exception as e:
        if os.path.exists(persistent_file_path):
            os.remove(persistent_file_path)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Batch prediction calculation failed: {str(e)}")
        
    return FileResponse(
        path=predicted_file_path,
        media_type="application/octet-stream",
        filename=f"predicted_{file.filename}"
    )
