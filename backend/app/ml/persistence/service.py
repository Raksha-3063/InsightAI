import os
import joblib
from typing import Any
from app.config import settings

# Create models upload directory if it does not exist
MODELS_DIR = os.path.join(settings.UPLOAD_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def save_model_pipeline(model_id: str, pipeline_obj: Any) -> str:
    """
    Serialize and save a scikit-learn/xgboost pipeline (or model) to local storage.
    """
    file_path = os.path.join(MODELS_DIR, f"{model_id}.joblib")
    joblib.dump(pipeline_obj, file_path)
    return file_path

def load_model_pipeline(file_path: str) -> Any:
    """
    Load and deserialize a pipeline/model from local storage.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Model file not found at path: {file_path}")
    return joblib.load(file_path)

def delete_model_pipeline(file_path: str):
    """
    Remove a serialized model file from local storage.
    """
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error removing model file {file_path}: {e}")
            raise e
