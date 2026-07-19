import os
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, status, Query
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from backend.app.database.connection import db_helper
from backend.app.auth.routes import get_current_user
from backend.app.models.user import User
from backend.app.routes.dataset import load_dataset_df

from backend.app.ai.context.builder import build_workspace_context
from backend.app.ai.services.copilot import ask_copilot_chat
from backend.app.ai.reports.generator import generate_report_markdown, convert_md_to_html
from backend.app.ai.recommendations.engine import generate_ai_recommendations
from backend.app.ai.history.service import list_conversations, get_conversation, delete_conversation, search_conversations
from backend.app.config import settings
from backend.app.tasks.jobs import ai_report_task

router = APIRouter()

# Rate limit simple tracker in memory
# IP/User ID -> list of timestamps
rate_limits: Dict[str, List[datetime]] = {}

def check_rate_limit(user_id: str):
    """
    Simple sliding-window rate limiter (max 30 requests per minute).
    """
    now = datetime.now(timezone.utc)
    if user_id not in rate_limits:
        rate_limits[user_id] = []
        
    # Filter timestamps within the last 60 seconds
    rate_limits[user_id] = [t for t in rate_limits[user_id] if (now - t).total_seconds() < 60]
    
    if len(rate_limits[user_id]) >= 30:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 30 AI copilot requests per minute."
        )
        
    rate_limits[user_id].append(now)

class ChatRequest(BaseModel):
    message: str
    conversationId: Optional[str] = None
    datasetId: str

class ReportRequest(BaseModel):
    datasetId: str
    format: str = "markdown"  # markdown, html, pdf

class RecommendationsRequest(BaseModel):
    datasetId: str

class ContextRequest(BaseModel):
    datasetId: str

@router.post("/{projectId}/ai/chat")
async def copilot_chat(
    projectId: str,
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId) or not ObjectId.is_valid(request.datasetId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")
        
    check_rate_limit(str(current_user.id))
    
    # Prompt size guard
    if len(request.message) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message exceeds length limit of 1000 characters."
        )
        
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    dataset_doc = await db_helper.db.datasets.find_one({"_id": ObjectId(request.datasetId), "projectId": projectId})
    if not dataset_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
        
    res = await ask_copilot_chat(
        project_id=projectId,
        dataset_doc=dataset_doc,
        message=request.message,
        conversation_id=request.conversationId,
        db=db_helper.db
    )
    return res

@router.post("/{projectId}/ai/report")
async def generate_executive_report(
    projectId: str,
    request: ReportRequest,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId) or not ObjectId.is_valid(request.datasetId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")
        
    check_rate_limit(str(current_user.id))
    
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    dataset_doc = await db_helper.db.datasets.find_one({"_id": ObjectId(request.datasetId), "projectId": projectId})
    if not dataset_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
        
    if settings.CELERY_ENABLED:
        job_oid = ObjectId()
        job_id = str(job_oid)
        job_doc = {
            "_id": job_oid,
            "projectId": projectId,
            "jobType": "report_generation",
            "status": "pending",
            "createdDate": datetime.now(timezone.utc)
        }
        await db_helper.db.background_jobs.insert_one(job_doc)
        
        ai_report_task.delay(
            job_id=job_id,
            project_id=projectId,
            dataset_id=request.datasetId,
            report_format=request.format
        )
        return {
            "jobId": job_id,
            "status": "pending"
        }

    # Synchronous Fallback Execution
    context = await build_workspace_context(projectId, dataset_doc, db_helper.db)
    md_report = generate_report_markdown(context)
    
    if request.format == "html":
        html_report = convert_md_to_html(md_report, project["projectName"])
        return {"report": html_report, "format": "html"}
    elif request.format == "pdf":
        html_report = convert_md_to_html(md_report, project["projectName"])
        return {"report": html_report, "format": "pdf"}
        
    return {"report": md_report, "format": "markdown"}

@router.get("/{projectId}/ai/history")
async def list_conversations_history(
    projectId: str,
    query: Optional[str] = Query(None, alias="q"),
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID")
        
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    if query:
        return await search_conversations(projectId, query, db_helper.db)
    return await list_conversations(projectId, db_helper.db)

@router.get("/{projectId}/ai/history/{conversationId}")
async def get_conversation_details(
    projectId: str,
    conversationId: str,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId) or not ObjectId.is_valid(conversationId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")
        
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    conv = await get_conversation(conversationId, db_helper.db)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation session not found")
        
    return conv

@router.delete("/{projectId}/ai/history/{conversationId}")
async def remove_conversation(
    projectId: str,
    conversationId: str,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId) or not ObjectId.is_valid(conversationId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")
        
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    deleted = await delete_conversation(conversationId, db_helper.db)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation session not found")
        
    return {"status": "success", "message": "Conversation history deleted."}

@router.post("/{projectId}/ai/recommendations")
async def copilot_recommendations(
    projectId: str,
    request: RecommendationsRequest,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId) or not ObjectId.is_valid(request.datasetId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")
        
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    dataset_doc = await db_helper.db.datasets.find_one({"_id": ObjectId(request.datasetId), "projectId": projectId})
    if not dataset_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
        
    context = await build_workspace_context(projectId, dataset_doc, db_helper.db)
    return generate_ai_recommendations(context)

@router.post("/{projectId}/ai/context")
async def copilot_context(
    projectId: str,
    request: ContextRequest,
    current_user: User = Depends(get_current_user)
):
    if not ObjectId.is_valid(projectId) or not ObjectId.is_valid(request.datasetId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")
        
    project = await db_helper.db.projects.find_one({"_id": ObjectId(projectId), "userId": current_user.id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    dataset_doc = await db_helper.db.datasets.find_one({"_id": ObjectId(request.datasetId), "projectId": projectId})
    if not dataset_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
        
    return await build_workspace_context(projectId, dataset_doc, db_helper.db)
