import os
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.concurrency import run_in_threadpool
from bson import ObjectId
from datetime import datetime
from backend.app.database.connection import db_helper
from backend.app.schemas.dataset import DatasetResponse
from backend.app.auth.routes import get_current_user
from backend.app.models.user import User
from backend.app.services.parser import parse_file_metadata
from backend.app.config import settings

router = APIRouter()

@router.post("/{projectId}/datasets/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    projectId: str, 
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_user)
):
    # Validate project ID format
    if not ObjectId.is_valid(projectId):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )

    # Check project exists and belongs to current user
    project = await db_helper.db.projects.find_one({
        "_id": ObjectId(projectId),
        "userId": current_user.id
    })
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Validate file extension
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in [".csv", ".xlsx", ".xls"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file extension. Only CSV and Excel (.xlsx, .xls) are supported."
        )

    # Create safe local storage path
    safe_filename = f"{projectId}_{int(datetime.utcnow().timestamp())}_{filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    # Save file to disk
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Parse metadata inside threadpool to prevent blocking the event loop
    try:
        metadata = await run_in_threadpool(parse_file_metadata, file_path, file_ext)
    except Exception as e:
        # Clean up file on failure
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse dataset file: {str(e)}"
        )

    # Build dataset document
    dataset_dict = {
        "projectId": projectId,
        "fileName": filename,
        "filePath": file_path,
        "rows": metadata["rows"],
        "columns": metadata["columns"],
        "missingValues": metadata["missingValues"],
        "duplicateRows": metadata["duplicateRows"],
        "size": metadata["size"],
        "columnTypes": metadata["columnTypes"],
        "numericalColumns": metadata["numericalColumns"],
        "categoricalColumns": metadata["categoricalColumns"],
        "dateColumns": metadata["dateColumns"],
        "uploadDate": datetime.utcnow()
    }

    # Save to MongoDB
    result = await db_helper.db.datasets.insert_one(dataset_dict)
    dataset_dict["_id"] = str(result.inserted_id)

    return DatasetResponse(**dataset_dict)
