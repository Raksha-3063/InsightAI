from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Annotated
from pydantic import BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]

class ModelRecord(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    projectId: PyObjectId
    datasetId: PyObjectId
    modelName: str
    algorithm: str
    taskType: str
    targetColumn: Optional[str] = None
    features: List[str]
    hyperparameters: Dict[str, Any]
    metrics: Dict[str, Any]
    filePath: str
    trainingTime: float
    featureImportance: List[Dict[str, Any]] = Field(default_factory=list)
    createdDate: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
