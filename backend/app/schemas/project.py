from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class ProjectCreate(BaseModel):
    projectName: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class ProjectResponse(BaseModel):
    id: str = Field(..., alias="_id")
    projectName: str
    description: Optional[str]
    userId: str
    createdAt: datetime

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }
