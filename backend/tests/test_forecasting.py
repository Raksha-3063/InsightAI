import pytest
from httpx import AsyncClient

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def auth_header(client: AsyncClient):
    # Register test user
    reg_payload = {"name": "Forecasting User", "email": "testfc@example.com", "password": "password123"}
    await client.post("/api/auth/register", json=reg_payload)
    
    # Login
    login_payload = {"email": "testfc@example.com", "password": "password123"}
    response = await client.post("/api/auth/login", json=login_payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def project_id(client: AsyncClient, auth_header):
    # Create project
    proj_payload = {"projectName": "FC Project", "description": "Testing Time Series & XAI"}
    response = await client.post("/api/projects", json=proj_payload, headers=auth_header)
    return response.json()["_id"]

@pytest.fixture
async def ts_dataset(client: AsyncClient, auth_header, project_id):
    # Create a mock sequential daily sales dataset
    csv_content = (
        "Date,Sales,StoreOpen,Promo\n"
        "2026-01-01,100,1,1\n"
        "2026-01-02,120,1,1\n"
        "2026-01-03,110,1,0\n"
        "2026-01-04,130,1,0\n"
        "2026-01-05,140,1,1\n"
        "2026-01-06,150,1,1\n"
        "2026-01-07,160,1,0\n"
        "2026-01-08,170,1,0\n"
        "2026-01-09,180,1,1\n"
        "2026-01-10,190,1,1\n"
        "2026-01-11,200,1,0\n"
        "2026-01-12,210,1,0\n"
    )
    file_bytes = csv_content.encode("utf-8")
    files = {"file": ("ts_data.csv", file_bytes, "text/csv")}
    
    response = await client.post(
        f"/api/projects/{project_id}/datasets/upload",
        files=files,
        headers=auth_header
    )
    return response.json()

@pytest.mark.anyio
async def test_time_series_detection(client: AsyncClient, auth_header, project_id, ts_dataset):
    response = await client.get(
        f"/api/projects/{project_id}/forecast/detect?datasetId={ts_dataset['_id']}",
        headers=auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["isFeasible"] is True
    assert data["datetimeColumn"] == "Date"
    assert data["suggestedTarget"] == "Sales"

@pytest.mark.anyio
async def test_forecasting_training_and_visuals(client: AsyncClient, auth_header, project_id, ts_dataset):
    train_payload = {
        "datasetId": ts_dataset["_id"],
        "dateColumn": "Date",
        "targetColumn": "Sales",
        "algorithm": "arima",
        "horizon": 5,
        "confidenceLevel": 0.95,
        "seasonalPeriod": 3,
        "trainRatio": 0.8
    }
    
    response = await client.post(
        f"/api/projects/{project_id}/forecast/train",
        json=train_payload,
        headers=auth_header
    )
    assert response.status_code == 201
    model_data = response.json()
    assert model_data["algorithm"] == "arima"
    assert "mae" in model_data["metrics"]
    
    model_id = model_data["_id"]
    
    # Visuals endpoint
    vis_res = await client.get(
        f"/api/projects/{project_id}/forecast/models/{model_id}/visuals",
        headers=auth_header
    )
    assert vis_res.status_code == 200
    vis_data = vis_res.json()
    assert "historical" in vis_data
    assert "forecast" in vis_data
    assert len(vis_data["forecast"]) == 5

@pytest.mark.anyio
async def test_ml_model_explainability_and_recommendations(client: AsyncClient, auth_header, project_id, ts_dataset):
    # First, train a classification model on Promo based on Sales and StoreOpen
    train_payload = {
        "datasetId": ts_dataset["_id"],
        "targetColumn": "Promo",
        "features": ["Sales", "StoreOpen"],
        "algorithm": "random_forest",
        "hyperparameters": {"n_estimators": 5, "max_depth": 2},
        "splitRatio": 0.2,
        "randomState": 42
    }
    train_res = await client.post(
        f"/api/projects/{project_id}/models/train",
        json=train_payload,
        headers=auth_header
    )
    assert train_res.status_code == 201
    model_id = train_res.json()["_id"]
    
    # 1. Explanations API (SHAP & LIME)
    exp_res = await client.get(
        f"/api/projects/{project_id}/models/{model_id}/explanations?rowIndex=1",
        headers=auth_header
    )
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert "shap" in exp_data
    assert "lime" in exp_data
    assert len(exp_data["lime"]) > 0
    assert "globalImportance" in exp_data["shap"]
    
    # 2. Recommendations API
    rec_res = await client.get(
        f"/api/projects/{project_id}/models/{model_id}/recommendations",
        headers=auth_header
    )
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    assert "recommendations" in rec_data
    assert len(rec_data["recommendations"]) > 0
