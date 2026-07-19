import pytest
from httpx import AsyncClient
from backend.app.database.connection import db_helper
from backend.app.ai.context.builder import build_workspace_context
from backend.app.ai.prompts.templates import format_dataset_summary_prompt

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def auth_header(client: AsyncClient):
    reg_payload = {"name": "AI User", "email": "testai@example.com", "password": "password123"}
    await client.post("/api/auth/register", json=reg_payload)
    
    login_payload = {"email": "testai@example.com", "password": "password123"}
    response = await client.post("/api/auth/login", json=login_payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def project_id(client: AsyncClient, auth_header):
    proj_payload = {"projectName": "AI Workspace", "description": "Testing AI Copilot Capabilities"}
    response = await client.post("/api/projects", json=proj_payload, headers=auth_header)
    return response.json()["_id"]

@pytest.fixture
async def ai_dataset(client: AsyncClient, auth_header, project_id):
    csv_content = (
        "Age,Salary,Target\n"
        "25,50000,0\n"
        "30,60000,1\n"
        "35,70000,0\n"
        "40,80000,1\n"
        "45,90000,0\n"
    )
    file_bytes = csv_content.encode("utf-8")
    files = {"file": ("ai_test.csv", file_bytes, "text/csv")}
    
    response = await client.post(
        f"/api/projects/{project_id}/datasets/upload",
        files=files,
        headers=auth_header
    )
    return response.json()

@pytest.mark.anyio
async def test_context_engine_and_prompts(project_id, ai_dataset):
    # Test context builder
    context = await build_workspace_context(project_id, ai_dataset, db_helper.db)
    assert context["datasetInfo"]["fileName"] == "ai_test.csv"
    assert context["datasetInfo"]["rowsCount"] == 5
    assert len(context["datasetInfo"]["numericalColumns"]) == 3
    
    # Test prompt templates
    prompt = format_dataset_summary_prompt(context)
    assert "ai_test.csv" in prompt
    assert "Total Records" or "observations" in prompt

@pytest.mark.anyio
async def test_ai_copilot_chat(client: AsyncClient, auth_header, project_id, ai_dataset):
    chat_payload = {
        "message": "Can you summarize my dataset details?",
        "datasetId": ai_dataset["_id"]
    }
    
    response = await client.post(
        f"/api/projects/{project_id}/ai/chat",
        json=chat_payload,
        headers=auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert "conversationId" in data
    assert "response" in data
    assert "Summary" in data["response"]
    
    conv_id = data["conversationId"]
    
    # Verify message logged in conversation history
    history_res = await client.get(
        f"/api/projects/{project_id}/ai/history/{conv_id}",
        headers=auth_header
    )
    assert history_res.status_code == 200
    history_data = history_res.json()
    assert len(history_data["messages"]) == 2
    assert history_data["messages"][0]["role"] == "user"
    assert history_data["messages"][1]["role"] == "assistant"
    
    # Search history
    search_res = await client.get(
        f"/api/projects/{project_id}/ai/history?q=summarize",
        headers=auth_header
    )
    assert search_res.status_code == 200
    assert len(search_res.json()) > 0
    
    # Delete history
    delete_res = await client.delete(
        f"/api/projects/{project_id}/ai/history/{conv_id}",
        headers=auth_header
    )
    assert delete_res.status_code == 200

@pytest.mark.anyio
async def test_executive_report_generation(client: AsyncClient, auth_header, project_id, ai_dataset):
    report_payload = {
        "datasetId": ai_dataset["_id"],
        "format": "html"
    }
    
    response = await client.post(
        f"/api/projects/{project_id}/ai/report",
        json=report_payload,
        headers=auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["format"] == "html"
    assert "<html" in data["report"]
    assert "tailwindcss" in data["report"]

@pytest.mark.anyio
async def test_recommendations_engine(client: AsyncClient, auth_header, project_id, ai_dataset):
    rec_payload = {
        "datasetId": ai_dataset["_id"]
    }
    
    response = await client.post(
        f"/api/projects/{project_id}/ai/recommendations",
        json=rec_payload,
        headers=auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "category" in data[0]
    assert "evidence" in data[0]
