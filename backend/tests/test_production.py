import pytest
from httpx import AsyncClient
from app.database.connection import db_helper

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def prod_auth_header(client: AsyncClient):
    reg_payload = {"name": "Prod Eng", "email": "prod@example.com", "password": "password123"}
    await client.post("/api/auth/register", json=reg_payload)
    
    login_payload = {"email": "prod@example.com", "password": "password123"}
    response = await client.post("/api/auth/login", json=login_payload)
    return response.json()

@pytest.mark.anyio
async def test_readiness_and_metrics(client: AsyncClient):
    # Test readiness GET /ready
    ready_res = await client.get("/ready")
    assert ready_res.status_code == 200
    assert ready_res.json()["status"] == "ready"
    assert "database" in ready_res.json()
    
    # Test metrics GET /metrics
    metrics_res = await client.get("/metrics")
    assert metrics_res.status_code == 200
    assert "insightai_request_count_total" in metrics_res.text

@pytest.mark.anyio
async def test_jwt_refresh_flow(client: AsyncClient, prod_auth_header):
    refresh_token = prod_auth_header["refresh_token"]
    assert refresh_token is not None
    
    # Trigger refresh
    refresh_res = await client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_res.status_code == 200
    data = refresh_res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    
    # Verify new token works
    profile_res = await client.get("/api/auth/profile", headers={"Authorization": f"Bearer {data['access_token']}"})
    assert profile_res.status_code == 200
    assert profile_res.json()["email"] == "prod@example.com"

@pytest.mark.anyio
async def test_rate_limiting_middleware(client: AsyncClient):
    import os
    os.environ["TESTING"] = "false"
    try:
        responses = []
        for _ in range(65):
            res = await client.get("/api/auth/profile")
            responses.append(res.status_code)
            if res.status_code == 429:
                break
                
        assert 429 in responses
    finally:
        os.environ["TESTING"] = "true"

@pytest.mark.anyio
async def test_file_upload_size_validation(client: AsyncClient, prod_auth_header):
    auth_header = {"Authorization": f"Bearer {prod_auth_header['access_token']}"}
    
    # Create project first
    proj_res = await client.post(
        "/api/projects",
        json={"projectName": "Prod Project", "description": "Testing secure uploads"},
        headers=auth_header
    )
    proj_id = proj_res.json()["_id"]
    
    # Create fake payload > 50MB (represented by mock larger content-length header)
    headers = {
        **auth_header,
        "Content-Length": str(100 * 1024 * 1024) # 100MB
    }
    
    files = {"file": ("huge_dataset.csv", b"dummy content", "text/csv")}
    
    upload_res = await client.post(
        f"/api/projects/{proj_id}/datasets/upload",
        files=files,
        headers=headers
    )
    assert upload_res.status_code == 413
    assert "exceeds" in upload_res.json()["detail"]
