import pytest
import os
import io
from httpx import AsyncClient

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def auth_header(client: AsyncClient):
    # Register a test user
    reg_payload = {"name": "Test User", "email": "testanalytics@example.com", "password": "password123"}
    await client.post("/api/auth/register", json=reg_payload)
    
    # Login
    login_payload = {"email": "testanalytics@example.com", "password": "password123"}
    response = await client.post("/api/auth/login", json=login_payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def project_id(client: AsyncClient, auth_header):
    # Create project
    proj_payload = {"projectName": "Analytics Project", "description": "Testing Phase 2 EDA logic"}
    response = await client.post("/api/projects", json=proj_payload, headers=auth_header)
    return response.json()["_id"]

@pytest.fixture
async def uploaded_dataset(client: AsyncClient, auth_header, project_id):
    # Create a mock CSV with missing values, duplicates, and outliers
    csv_content = (
        "Age,Salary,Target,City\n"
        "25,50000,1,New York\n"
        "30,60000,0,Chicago\n"
        "35,,1,New York\n"  # missing Salary
        "30,60000,0,Chicago\n"  # duplicate row
        "120,200000,1,Miami\n"  # outlier Age & Salary
    )
    
    file_bytes = csv_content.encode("utf-8")
    files = {"file": ("test_data.csv", file_bytes, "text/csv")}
    
    response = await client.post(
        f"/api/projects/{project_id}/datasets/upload",
        files=files,
        headers=auth_header
    )
    return response.json()

@pytest.mark.anyio
async def test_dataset_profiling(client: AsyncClient, auth_header, project_id, uploaded_dataset):
    response = await client.get(
        f"/api/projects/{project_id}/datasets/profile",
        headers=auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rows"] == 5
    assert data["columns"] == 4
    assert data["missingValues"] == 1
    assert data["duplicateRows"] == 1
    assert "Age" in data["numericalColumns"]
    assert "City" in data["categoricalColumns"]
    assert data["targetSuggestion"] == "Target"

@pytest.mark.anyio
async def test_dataset_statistics_and_correlations(client: AsyncClient, auth_header, project_id, uploaded_dataset):
    # Statistics
    stats_res = await client.get(
        f"/api/projects/{project_id}/datasets/statistics",
        headers=auth_header
    )
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "Age" in stats["numerical"]
    assert "City" in stats["categorical"]
    assert stats["numerical"]["Age"]["mean"] == (25 + 30 + 35 + 30 + 120) / 5.0
    assert stats["categorical"]["City"]["uniqueValues"] == 3

    # Correlations
    corr_res = await client.get(
        f"/api/projects/{project_id}/datasets/correlations",
        headers=auth_header
    )
    assert corr_res.status_code == 200
    corrs = corr_res.json()
    assert len(corrs["pearson"]) == 3  # Age, Salary, Target

@pytest.mark.anyio
async def test_dataset_visualizations(client: AsyncClient, auth_header, project_id, uploaded_dataset):
    # Histogram
    hist_res = await client.get(
        f"/api/projects/{project_id}/datasets/visualizations?col=Age&chart_type=histogram",
        headers=auth_header
    )
    assert hist_res.status_code == 200
    assert len(hist_res.json()) > 0

    # Box Plot
    box_res = await client.get(
        f"/api/projects/{project_id}/datasets/visualizations?col=Age&chart_type=boxplot",
        headers=auth_header
    )
    assert box_res.status_code == 200
    assert box_res.json()["median"] == 30.0

@pytest.mark.anyio
async def test_dataset_health_and_insights(client: AsyncClient, auth_header, project_id, uploaded_dataset):
    # Health Score
    health_res = await client.get(
        f"/api/projects/{project_id}/datasets/health-score",
        headers=auth_header
    )
    assert health_res.status_code == 200
    health = health_res.json()
    assert health["score"] < 100  # because of duplicates and missing values
    assert len(health["warnings"]) > 0

    # Insights
    insights_res = await client.get(
        f"/api/projects/{project_id}/datasets/insights",
        headers=auth_header
    )
    assert insights_res.status_code == 200
    insights = insights_res.json()
    assert len(insights) > 0
    assert any(ins["title"] == "Target Column Suggestion" for ins in insights)

@pytest.mark.anyio
async def test_dataset_cleaning_and_revert(client: AsyncClient, auth_header, project_id, uploaded_dataset):
    # 1. Impute missing Salary with mean
    clean_payload = {
        "opType": "impute_missing",
        "params": {"column": "Salary", "strategy": "mean"}
    }
    clean_res = await client.post(
        f"/api/projects/{project_id}/datasets/clean",
        json=clean_payload,
        headers=auth_header
    )
    assert clean_res.status_code == 200
    clean_data = clean_res.json()
    assert clean_data["missingValues"] == 0
    assert len(clean_data["cleaningHistory"]) == 1

    # 2. Revert the operation
    revert_res = await client.post(
        f"/api/projects/{project_id}/datasets/revert",
        headers=auth_header
    )
    assert revert_res.status_code == 200
    revert_data = revert_res.json()
    assert revert_data["missingValues"] == 1
    assert len(revert_data["cleaningHistory"]) == 0

    # Clean up uploaded files on disk
    await client.delete(
        f"/api/projects/{project_id}/datasets",
        headers=auth_header
    )
