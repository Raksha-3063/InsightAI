import pytest
import io

@pytest.mark.asyncio
async def test_upload_dataset_csv_success(client):
    # Log in
    login_data = {"email": "test@example.com", "password": "password123"}
    login_resp = await client.post("/api/auth/login", json=login_data)
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get project ID
    proj_resp = await client.get("/api/projects", headers=headers)
    project_id = proj_resp.json()[0]["_id"]

    # Mock file contents
    csv_data = b"id,name,salary,hire_date\n1,Alice,50000,2026-01-01\n2,Bob,60000,2026-02-01\n3,Charlie,70000,\n1,Alice,50000,2026-01-01\n"
    file = {"file": ("employees.csv", csv_data, "text/csv")}

    # Upload
    response = await client.post(
        f"/api/projects/{project_id}/datasets/upload", 
        files=file, 
        headers=headers
    )
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["fileName"] == "employees.csv"
    assert json_data["rows"] == 4
    assert json_data["columns"] == 4
    assert json_data["missingValues"] == 1  # hire_date is empty for Charlie
    assert json_data["duplicateRows"] == 1  # Alice row is duplicate
    assert "numerical" in json_data["columnTypes"]["salary"]
