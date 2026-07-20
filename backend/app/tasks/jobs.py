import os
import asyncio
import logging
import pandas as pd
from datetime import datetime, timezone
from bson import ObjectId
from typing import Dict, Any, List, Optional

from app.config import settings
from app.database.connection import db_helper, connect_to_mongo
from app.tasks.worker import celery_app
from app.ml.tracking import log_experiment_run

# ML Training functions
from app.ml.training.regression import train_regression_model
from app.ml.training.classification import train_classification_model
from app.ml.training.clustering import train_clustering_model
from app.ml.persistence.service import save_model_pipeline, load_model_pipeline

# Forecasting & Explainability functions
from app.ml.forecasting.engine import train_forecasting_model
from app.ml.explainability.service import get_shap_explanations, get_lime_explanation
from app.ml.prediction.service import predict_batch
from app.ai.context.builder import build_workspace_context
from app.ai.reports.generator import generate_report_markdown, convert_md_to_html

logger = logging.getLogger("celery_jobs")

def run_async(coro):
    """
    Helper to run asynchronous coroutines in Celery synchronous workers.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

async def init_db_connection():
    """
    Ensures MongoDB is initialized in the worker process.
    """
    if db_helper.db is None:
        await connect_to_mongo()

@celery_app.task(name="app.tasks.jobs.train_ml_model_task")
def train_ml_model_task(
    model_id: str,
    project_id: str,
    dataset_id: str,
    file_path: str,
    algorithm: str,
    features: List[str],
    target_column: Optional[str],
    hyperparameters: Dict[str, Any],
    split_ratio: float,
    random_state: int,
    stratified: bool,
    num_cols: List[str],
    cat_cols: List[str],
    task_type: str
):
    logger.info(f"Starting Celery background job to train model {model_id}")
    
    # 1. Initialize MongoDB inside Celery worker
    run_async(init_db_connection())
    
    try:
        # Update model status in MongoDB to "running"
        run_async(db_helper.db.models.update_one(
            {"_id": ObjectId(model_id)},
            {"$set": {"status": "running", "startedDate": datetime.now(timezone.utc)}}
        ))
        
        # Load dataset
        df = pd.read_csv(file_path)
        
        # 2. Fit model based on task type
        if task_type == "regression":
            pipeline, metrics, visuals, importance, train_time = train_regression_model(
                df, features, target_column, algorithm, hyperparameters,
                split_ratio, random_state, num_cols, cat_cols
            )
            target_encoder = None
            
        elif task_type == "classification":
            pipeline, target_encoder, metrics, visuals, importance, train_time = train_classification_model(
                df, features, target_column, algorithm, hyperparameters,
                split_ratio, random_state, stratified, num_cols, cat_cols
            )
            
        else: # clustering
            pipeline, metrics, visuals, train_time = train_clustering_model(
                df, features, algorithm, hyperparameters,
                random_state, num_cols, cat_cols
            )
            target_encoder = None
            importance = []
            
        # 3. Save pipeline locally
        save_data = {
            "pipeline": pipeline,
            "target_encoder": target_encoder
        }
        saved_file_path = save_model_pipeline(model_id, save_data)
        
        # 4. Save visualization coordinates in separate collection
        visuals_dict = {
            "modelId": model_id,
            "visualizations": visuals,
            "createdDate": datetime.now(timezone.utc)
        }
        run_async(db_helper.db.model_visualizations.replace_one(
            {"modelId": model_id}, visuals_dict, upsert=True
        ))
        
        # 5. MLflow Tracking logging
        artifacts = {"pipeline": saved_file_path}
        run_id = log_experiment_run(
            project_id=project_id,
            model_name=f"{algorithm}_{model_id[:5]}",
            algorithm=algorithm,
            hyperparameters=hyperparameters,
            metrics=metrics,
            artifacts=artifacts
        )
        
        # 6. Update Model document as completed
        run_async(db_helper.db.models.update_one(
            {"_id": ObjectId(model_id)},
            {"$set": {
                "status": "completed",
                "metrics": metrics,
                "filePath": saved_file_path,
                "trainingTime": train_time,
                "featureImportance": importance,
                "mlflowRunId": run_id,
                "completedDate": datetime.now(timezone.utc)
            }}
        ))
        logger.info(f"Model {model_id} training completed successfully.")
        
    except Exception as e:
        logger.error(f"Background training failed for model {model_id}: {str(e)}")
        run_async(db_helper.db.models.update_one(
            {"_id": ObjectId(model_id)},
            {"$set": {
                "status": "failed",
                "error": str(e),
                "completedDate": datetime.now(timezone.utc)
            }}
        ))

@celery_app.task(name="app.tasks.jobs.train_forecast_task")
def train_forecast_task(
    forecast_id: str,
    project_id: str,
    dataset_id: str,
    file_path: str,
    target_column: str,
    date_column: str,
    algorithm: str,
    horizon: int,
    seasonal_period: int,
    confidence_level: float,
    train_ratio: float
):
    logger.info(f"Starting Celery background job to train forecast model {forecast_id}")
    run_async(init_db_connection())
    
    try:
        run_async(db_helper.db.forecasts.update_one(
            {"_id": ObjectId(forecast_id)},
            {"$set": {"status": "running", "startedDate": datetime.now(timezone.utc)}}
        ))
        
        # Load dataset
        df = pd.read_csv(file_path)
        
        # Fit forecasting model
        model, predictions, evaluation_metrics, forecast_visuals = train_forecasting_model(
            df=df,
            date_col=date_column,
            target_col=target_column,
            algorithm=algorithm,
            horizon=horizon,
            seasonal_period=seasonal_period,
            confidence_level=confidence_level,
            train_ratio=train_ratio
        )
        
        # Save forecast pipeline
        saved_file_path = save_model_pipeline(f"forecast_{forecast_id}", {"model": model})
        
        # Save visuals
        visuals_dict = {
            "forecastId": forecast_id,
            "visualizations": forecast_visuals,
            "createdDate": datetime.now(timezone.utc)
        }
        run_async(db_helper.db.forecast_visualizations.replace_one(
            {"forecastId": forecast_id}, visuals_dict, upsert=True
        ))
        
        # Update database record
        run_async(db_helper.db.forecasts.update_one(
            {"_id": ObjectId(forecast_id)},
            {"$set": {
                "status": "completed",
                "metrics": evaluation_metrics,
                "filePath": saved_file_path,
                "completedDate": datetime.now(timezone.utc)
            }}
        ))
        logger.info(f"Forecast model {forecast_id} training completed successfully.")
        
    except Exception as e:
        logger.error(f"Background forecast training failed for {forecast_id}: {str(e)}")
        run_async(db_helper.db.forecasts.update_one(
            {"_id": ObjectId(forecast_id)},
            {"$set": {
                "status": "failed",
                "error": str(e),
                "completedDate": datetime.now(timezone.utc)
            }}
        ))

@celery_app.task(name="app.tasks.jobs.explainability_task")
def explainability_task(
    job_id: str,
    project_id: str,
    model_id: str,
    row_index: int
):
    logger.info(f"Starting explainability generation task {job_id}")
    run_async(init_db_connection())
    
    try:
        run_async(db_helper.db.background_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {"status": "running"}}
        ))
        
        # Load model metadata
        model_doc = run_async(db_helper.db.models.find_one({"_id": ObjectId(model_id)}))
        dataset_doc = run_async(db_helper.db.datasets.find_one({"_id": ObjectId(model_doc["datasetId"])}))
        
        df = pd.read_csv(dataset_doc["filePath"])
        X_train = df[model_doc["features"]]
        
        # Load pipeline
        save_data = load_model_pipeline(model_doc["filePath"])
        pipeline = save_data["pipeline"]
        
        # Get target instance
        if row_index < 0 or row_index >= len(df):
            row_index = 0
        instance = X_train.iloc[row_index]
        
        # Compute explainability
        shap_data = get_shap_explanations(pipeline, X_train)
        lime_data = get_lime_explanation(pipeline, X_train, instance)
        
        result_payload = {
            "shap": shap_data,
            "lime": lime_data,
            "featuresUsed": model_doc["features"],
            "targetInstance": instance.to_dict()
        }
        
        # Save result to background_jobs
        run_async(db_helper.db.background_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {
                "status": "completed",
                "result": result_payload,
                "completedDate": datetime.now(timezone.utc)
            }}
        ))
        
    except Exception as e:
        logger.error(f"Explainability task {job_id} failed: {str(e)}")
        run_async(db_helper.db.background_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {
                "status": "failed",
                "error": str(e),
                "completedDate": datetime.now(timezone.utc)
            }}
        ))

@celery_app.task(name="app.tasks.jobs.ai_report_task")
def ai_report_task(
    job_id: str,
    project_id: str,
    dataset_id: str,
    report_format: str
):
    logger.info(f"Starting AI report compilation task {job_id}")
    run_async(init_db_connection())
    
    try:
        run_async(db_helper.db.background_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {"status": "running"}}
        ))
        
        project = run_async(db_helper.db.projects.find_one({"_id": ObjectId(project_id)}))
        dataset_doc = run_async(db_helper.db.datasets.find_one({"_id": ObjectId(dataset_id)}))
        
        # Build workspace context
        context = run_async(build_workspace_context(project_id, dataset_doc, db_helper.db))
        
        md_report = generate_report_markdown(context)
        
        report_result = md_report
        if report_format in ["html", "pdf"]:
            report_result = convert_md_to_html(md_report, project["projectName"])
            
        result_payload = {
            "report": report_result,
            "format": report_format
        }
        
        run_async(db_helper.db.background_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {
                "status": "completed",
                "result": result_payload,
                "completedDate": datetime.now(timezone.utc)
            }}
        ))
        
    except Exception as e:
        logger.error(f"AI report task {job_id} failed: {str(e)}")
        run_async(db_helper.db.background_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {
                "status": "failed",
                "error": str(e),
                "completedDate": datetime.now(timezone.utc)
            }}
        ))

@celery_app.task(name="app.tasks.jobs.batch_prediction_task")
def batch_prediction_task(
    job_id: str,
    project_id: str,
    model_id: str,
    file_path: str
):
    logger.info(f"Starting batch prediction task {job_id}")
    run_async(init_db_connection())
    
    try:
        run_async(db_helper.db.background_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {"status": "running"}}
        ))
        
        # Load model
        model_doc = run_async(db_helper.db.models.find_one({"_id": ObjectId(model_id)}))
        save_data = load_model_pipeline(model_doc["filePath"])
        pipeline = save_data["pipeline"]
        target_encoder = save_data["target_encoder"]
        
        df = pd.read_csv(file_path)
        predictions = predict_batch(pipeline, target_encoder, df, model_doc["features"])
        
        run_async(db_helper.db.background_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {
                "status": "completed",
                "result": {"predictions": predictions},
                "completedDate": datetime.now(timezone.utc)
            }}
        ))
        
    except Exception as e:
        logger.error(f"Batch prediction task {job_id} failed: {str(e)}")
        run_async(db_helper.db.background_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {
                "status": "failed",
                "error": str(e),
                "completedDate": datetime.now(timezone.utc)
            }}
        ))
