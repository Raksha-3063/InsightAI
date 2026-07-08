from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict

class DatasetResponse(BaseModel):
    id: str = Field(..., alias="_id")
    projectId: str
    fileName: str
    filePath: str
    rows: int
    columns: int
    missingValues: int
    duplicateRows: int
    size: int
    columnTypes: Dict[str, str]
    numericalColumns: List[str]
    categoricalColumns: List[str]
    dateColumns: List[str]
    uploadDate: datetime

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }
