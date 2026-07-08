from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Annotated
from pydantic import BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]

class Project(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    projectName: str
    description: Optional[str] = None
    userId: PyObjectId
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
