import pytest

@pytest.mark.asyncio
async def test_create_project_success(client):
    # Log in first
    login_data = {"email": "test@example.com", "password": "password123"}
    login_resp = await client.post("/api/auth/login", json=login_data)
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    project_data = {
        "projectName": "Retail Sales Analytics",
        "description": "Analyze retail store metrics"
    }
    response = await client.post("/api/projects", json=project_data, headers=headers)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["projectName"] == project_data["projectName"]
    assert json_data["description"] == project_data["description"]
    assert "_id" in json_data
    assert "userId" in json_data

@pytest.mark.asyncio
async def test_list_projects_success(client):
    login_data = {"email": "test@example.com", "password": "password123"}
    login_resp = await client.post("/api/auth/login", json=login_data)
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/projects", headers=headers)
    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data) >= 1
    assert json_data[0]["projectName"] == "Retail Sales Analytics"
