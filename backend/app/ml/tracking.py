import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("mlflow_tracker")

try:
    import mlflow
    HAS_MLFLOW = True
except ImportError:
    HAS_MLFLOW = False

def log_experiment_run(
    project_id: str,
    model_name: str,
    algorithm: str,
    hyperparameters: Dict[str, Any],
    metrics: Dict[str, Any],
    artifacts: Optional[Dict[str, str]] = None
) -> Optional[str]:
    """
    Logs hyperparameters, validation metrics, and model artifacts to MLflow.
    Groups runs under a specific experiment per project: Project_{project_id}.
    Falls back gracefully if MLflow is not installed or the tracking server is unreachable.
    """
    if not HAS_MLFLOW:
        logger.info(f"[Mock Tracker] Project: {project_id} | Model: {model_name} | Alg: {algorithm} | Metrics: {metrics}")
        return None

    try:
        # Determine tracking URI (defaults to local sqlite DB)
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
        mlflow.set_tracking_uri(tracking_uri)
        
        # Group runs by project ID
        experiment_name = f"Project_{project_id}"
        mlflow.set_experiment(experiment_name)
        
        with mlflow.start_run(run_name=model_name) as run:
            # 1. Log parameters
            mlflow.log_param("algorithm", algorithm)
            for key, val in hyperparameters.items():
                mlflow.log_param(f"param_{key}", val)
                
            # 2. Log metrics
            for key, val in metrics.items():
                if isinstance(val, (int, float)):
                    mlflow.log_metric(key, float(val))
                    
            # 3. Log model file artifacts
            if artifacts:
                for art_name, art_path in artifacts.items():
                    if os.path.exists(art_path):
                        mlflow.log_artifact(art_path, artifact_path="models")
                        
            run_id = run.info.run_id
            logger.info(f"Successfully logged model run {model_name} to MLflow. Run ID: {run_id}")
            return run_id
            
    except Exception as e:
        logger.warning(f"MLflow tracking failed (falling back safely): {str(e)}")
        return None
