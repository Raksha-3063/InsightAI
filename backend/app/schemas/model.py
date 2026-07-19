from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class TrainRequest(BaseModel):
    datasetId: str
    targetColumn: Optional[str] = None  # None for clustering
    features: List[str]
    algorithm: str
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    splitRatio: float = 0.2
    randomState: int = 42
    stratified: bool = False

class PredictRequest(BaseModel):
    data: List[Dict[str, Any]]

class ModelResponse(BaseModel):
    id: str = Field(..., alias="_id")
    projectId: str
    datasetId: str
    modelName: str
    algorithm: str
    taskType: str
    targetColumn: Optional[str] = None
    features: List[str]
    hyperparameters: Dict[str, Any]
    metrics: Dict[str, Any]
    trainingTime: float
    featureImportance: List[Dict[str, Any]] = Field(default_factory=list)
    createdDate: datetime
    status: Optional[str] = "completed"

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }
