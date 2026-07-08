from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Annotated
from pydantic import BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]

class Dataset(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    projectId: PyObjectId
    fileName: str
    filePath: str
    rows: int
    columns: int
    missingValues: int
    duplicateRows: int
    size: int  # in bytes
    columnTypes: Dict[str, str]  # colName -> type
    numericalColumns: List[str]
    categoricalColumns: List[str]
    dateColumns: List[str]
    uploadDate: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
