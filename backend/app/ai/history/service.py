from datetime import datetime, timezone
from bson import ObjectId
from typing import List, Dict, Any, Optional

async def create_conversation(project_id: str, dataset_id: str, db: Any) -> str:
    """
    Creates a new conversation record in the database.
    """
    conv_oid = ObjectId()
    doc = {
        "_id": conv_oid,
        "projectId": project_id,
        "datasetId": dataset_id,
        "messages": [],
        "referencedModels": [],
        "createdDate": datetime.now(timezone.utc),
        "lastModified": datetime.now(timezone.utc)
    }
    await db.conversations.insert_one(doc)
    return str(conv_oid)

async def add_message(
    conversation_id: str,
    role: str,
    content: str,
    db: Any,
    referenced_models: Optional[List[str]] = None
) -> None:
    """
    Appends a new user or assistant message to the conversation.
    """
    now = datetime.now(timezone.utc)
    message_doc = {
        "role": role,
        "content": content,
        "timestamp": now
    }
    
    update_op: Dict[str, Any] = {
        "$push": {"messages": message_doc},
        "$set": {"lastModified": now}
    }
    
    if referenced_models:
        update_op["$addToSet"] = {"referencedModels": {"$each": referenced_models}}
        
    await db.conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        update_op
    )

async def get_conversation(conversation_id: str, db: Any) -> Optional[Dict[str, Any]]:
    """
    Retrieves a conversation history details by ID.
    """
    doc = await db.conversations.find_one({"_id": ObjectId(conversation_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
        # Format timestamps as ISO strings
        for msg in doc.get("messages", []):
            if isinstance(msg.get("timestamp"), datetime):
                msg["timestamp"] = msg["timestamp"].isoformat()
        if isinstance(doc.get("createdDate"), datetime):
            doc["createdDate"] = doc["createdDate"].isoformat()
        if isinstance(doc.get("lastModified"), datetime):
            doc["lastModified"] = doc["lastModified"].isoformat()
    return doc

async def list_conversations(project_id: str, db: Any) -> List[Dict[str, Any]]:
    """
    Lists all conversation sessions in a project, sorted by most recently modified.
    """
    cursor = db.conversations.find({"projectId": project_id}).sort("lastModified", -1)
    sessions = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        if isinstance(doc.get("createdDate"), datetime):
            doc["createdDate"] = doc["createdDate"].isoformat()
        if isinstance(doc.get("lastModified"), datetime):
            doc["lastModified"] = doc["lastModified"].isoformat()
        # Clean messages list to return a preview
        preview = doc.get("messages", [])
        doc["messagesCount"] = len(preview)
        doc["previewText"] = preview[-1]["content"][:60] + "..." if preview else "Empty conversation"
        doc.pop("messages", None)
        sessions.append(doc)
    return sessions

async def delete_conversation(conversation_id: str, db: Any) -> bool:
    """
    Deletes a conversation history from database.
    """
    res = await db.conversations.delete_one({"_id": ObjectId(conversation_id)})
    return res.deleted_count > 0

async def search_conversations(project_id: str, query: str, db: Any) -> List[Dict[str, Any]]:
    """
    Searches message contents for a matching text query inside a project.
    """
    cursor = db.conversations.find({
        "projectId": project_id,
        "messages.content": {"$regex": query, "$options": "i"}
    }).sort("lastModified", -1)
    
    sessions = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        if isinstance(doc.get("createdDate"), datetime):
            doc["createdDate"] = doc["createdDate"].isoformat()
        if isinstance(doc.get("lastModified"), datetime):
            doc["lastModified"] = doc["lastModified"].isoformat()
        preview = doc.get("messages", [])
        doc["messagesCount"] = len(preview)
        doc["previewText"] = preview[-1]["content"][:60] + "..." if preview else "Empty conversation"
        doc.pop("messages", None)
        sessions.append(doc)
    return sessions
