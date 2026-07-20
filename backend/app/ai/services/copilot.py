from bson import ObjectId
from typing import Dict, Any, List, Optional

from app.ai.context.builder import build_workspace_context
from app.ai.prompts.templates import COPILOT_SYSTEM_INSTRUCTION, format_general_chat_prompt
from app.ai.providers.gemini import call_gemini_api
from app.ai.history.service import create_conversation, add_message, get_conversation

async def ask_copilot_chat(
    project_id: str,
    dataset_doc: Dict[str, Any],
    message: str,
    conversation_id: Optional[str],
    db: Any
) -> Dict[str, Any]:
    """
    Orchestrates the chat session, builds context, calls the LLM, and logs message history.
    """
    # 1. Create session if not provided
    if not conversation_id:
        conversation_id = await create_conversation(project_id, str(dataset_doc["_id"]), db)
        
    # 2. Build workspace context
    context = await build_workspace_context(project_id, dataset_doc, db)
    
    # 3. Add User message to history
    await add_message(conversation_id, "user", message, db)
    
    # 4. Generate LLM prompt
    prompt = format_general_chat_prompt(message, context)
    
    # 5. Call LLM provider
    response_text = call_gemini_api(prompt, system_instruction=COPILOT_SYSTEM_INSTRUCTION)
    
    # 6. Add Assistant message to history
    # Identify referenced models if any
    referenced_models = []
    for model in context.get("machineLearningModels", []):
        if model["modelName"].lower() in message.lower() or model["algorithm"].lower() in message.lower():
            referenced_models.append(model["modelId"])
            
    await add_message(
        conversation_id=conversation_id,
        role="assistant",
        content=response_text,
        db=db,
        referenced_models=referenced_models
    )
    
    return {
        "conversationId": conversation_id,
        "response": response_text
    }
