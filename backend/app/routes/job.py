from fastapi import APIRouter, HTTPException, Depends, status
from bson import ObjectId
from typing import List, Dict, Any

from app.database.connection import db_helper
from app.auth.routes import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/{projectId}/jobs/{jobId}")
async def get_job_status(
    projectId: str,
    jobId: str,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId) or not ObjectId.is_valid(jobId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID formats")
        
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    job = await db_helper.db.background_jobs.find_one({"_id": ObjectId(jobId), "projectId": projectId})
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        
    job["_id"] = str(job["_id"])
    if "createdDate" in job and job["createdDate"]:
        job["createdDate"] = job["createdDate"].isoformat()
    if "completedDate" in job and job["completedDate"]:
        job["completedDate"] = job["completedDate"].isoformat()
        
    return job

@router.get("/{projectId}/jobs")
async def list_jobs(
    projectId: str,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format")
        
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    cursor = db_helper.db.background_jobs.find({"projectId": projectId}).sort("createdDate", -1).limit(20)
    jobs = []
    async for job in cursor:
        job["_id"] = str(job["_id"])
        if "createdDate" in job and job["createdDate"]:
            job["createdDate"] = job["createdDate"].isoformat()
        if "completedDate" in job and job["completedDate"]:
            job["completedDate"] = job["completedDate"].isoformat()
        jobs.append(job)
    return jobs
