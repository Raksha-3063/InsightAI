from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime, timezone
from bson import ObjectId
from backend.app.database.connection import db_helper
from backend.app.schemas.project import ProjectCreate, ProjectResponse
from backend.app.auth.routes import get_current_user
from backend.app.models.user import User

router = APIRouter()

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project_data: ProjectCreate, current_user: User = Depends(get_current_user)):
    new_project_dict = {
        "projectName": project_data.projectName,
        "description": project_data.description,
        "userId": current_user.id,
        "createdAt": datetime.now(timezone.utc)
    }
    
    result = await db_helper.db.projects.insert_one(new_project_dict)
    new_project_dict["_id"] = str(result.inserted_id)
    
    return ProjectResponse(**new_project_dict)

@router.get("", response_model=List[ProjectResponse])
async def list_projects(current_user: User = Depends(get_current_user)):
    cursor = db_helper.db.projects.find({"userId": current_user.id})
    projects = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        projects.append(ProjectResponse(**doc))
    return projects

@router.get("/{projectId}", response_model=ProjectResponse)
async def get_project(projectId: str, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(projectId):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    project_doc = await db_helper.db.projects.find_one({
        "_id": ObjectId(projectId),
        "userId": current_user.id
    })
    
    if not project_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
        
    project_doc["_id"] = str(project_doc["_id"])
    return ProjectResponse(**project_doc)
