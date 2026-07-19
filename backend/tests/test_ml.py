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
    reg_payload = {"name": "ML User", "email": "testml@example.com", "password": "password123"}
    await client.post("/api/auth/register", json=reg_payload)
    
    # Login
    login_payload = {"email": "testml@example.com", "password": "password123"}
    response = await client.post("/api/auth/login", json=login_payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def project_id(client: AsyncClient, auth_header):
    # Create project
    proj_payload = {"projectName": "ML Project", "description": "Testing Phase 3 ML logic"}
    response = await client.post("/api/projects", json=proj_payload, headers=auth_header)
    return response.json()["_id"]

@pytest.fixture
async def uploaded_dataset(client: AsyncClient, auth_header, project_id):
    # Create a mock CSV with missing values, categories, and numerical cols
    csv_content = (
        "Age,Salary,Target,Label,Group\n"
        "25,50000,1,Yes,A\n"
        "30,60000,0,No,B\n"
        "35,55000,1,Yes,A\n"
        "40,65000,0,No,C\n"
        "45,70000,1,Yes,B\n"
    )
    
    file_bytes = csv_content.encode("utf-8")
    files = {"file": ("test_ml.csv", file_bytes, "text/csv")}
    
    response = await client.post(
        f"/api/projects/{project_id}/datasets/upload",
        files=files,
        headers=auth_header
    )
    return response.json()

@pytest.mark.anyio
async def test_regression_training(client: AsyncClient, auth_header, project_id, uploaded_dataset):
    train_payload = {
        "datasetId": uploaded_dataset["_id"],
        "targetColumn": "Salary",
        "features": ["Age", "Target"],
        "algorithm": "linear_regression",
        "hyperparameters": {},
        "splitRatio": 0.2,
        "randomState": 42
    }
    
    response = await client.post(
        f"/api/projects/{project_id}/models/train",
        json=train_payload,
        headers=auth_header
    )
    assert response.status_code == 201
    data = response.json()
    assert data["algorithm"] == "linear_regression"
    assert data["taskType"] == "regression"
    assert "mae" in data["metrics"]
    assert "r2" in data["metrics"]
    assert len(data["featureImportance"]) > 0

@pytest.mark.anyio
async def test_classification_training_and_prediction(client: AsyncClient, auth_header, project_id, uploaded_dataset):
    # Train random_forest classification model
    train_payload = {
        "datasetId": uploaded_dataset["_id"],
        "targetColumn": "Label",
        "features": ["Age", "Salary"],
        "algorithm": "random_forest",
        "hyperparameters": {"n_estimators": 10, "max_depth": 3},
        "splitRatio": 0.2,
        "randomState": 42,
        "stratified": True
    }
    
    response = await client.post(
        f"/api/projects/{project_id}/models/train",
        json=train_payload,
        headers=auth_header
    )
    assert response.status_code == 201
    model_data = response.json()
    model_id = model_data["_id"]
    
    assert model_data["algorithm"] == "random_forest"
    assert model_data["taskType"] == "classification"
    assert "accuracy" in model_data["metrics"]
    
    # Test visuals endpoint
    visuals_res = await client.get(
        f"/api/projects/{project_id}/models/{model_id}/visuals",
        headers=auth_header
    )
    assert visuals_res.status_code == 200
    
    # Test Predict Manual endpoint
    predict_payload = {
        "data": [
            {"Age": 28, "Salary": 58000},
            {"Age": 48, "Salary": 75000}
        ]
    }
    pred_res = await client.post(
        f"/api/projects/{project_id}/models/{model_id}/predict",
        json=predict_payload,
        headers=auth_header
    )
    assert pred_res.status_code == 200
    pred_data = pred_res.json()
    assert len(pred_data["predictions"]) == 2
    # Verify values are mapped back to Yes/No labels
    assert pred_data["predictions"][0] in ["Yes", "No"]

    # Test Predict Batch file upload
    batch_csv = "Age,Salary\n32,62000\n44,68000\n"
    batch_bytes = batch_csv.encode("utf-8")
    files = {"file": ("batch.csv", batch_bytes, "text/csv")}
    
    batch_res = await client.post(
        f"/api/projects/{project_id}/models/{model_id}/predict/file",
        files=files,
        headers=auth_header
    )
    assert batch_res.status_code == 200
    assert "predicted_batch.csv" in batch_res.headers.get("content-disposition", "")
    assert len(batch_res.content) > 0

@pytest.mark.anyio
async def test_clustering_training(client: AsyncClient, auth_header, project_id, uploaded_dataset):
    train_payload = {
        "datasetId": uploaded_dataset["_id"],
        "features": ["Age", "Salary"],
        "algorithm": "kmeans",
        "hyperparameters": {"n_clusters": 2},
        "splitRatio": 0.2,
        "randomState": 42
    }
    
    response = await client.post(
        f"/api/projects/{project_id}/models/train",
        json=train_payload,
        headers=auth_header
    )
    assert response.status_code == 201
    model_data = response.json()
    assert model_data["algorithm"] == "kmeans"
    assert model_data["taskType"] == "clustering"
    assert "silhouette" in model_data["metrics"]

@pytest.mark.anyio
async def test_models_comparison_and_deletion(client: AsyncClient, auth_header, project_id, uploaded_dataset):
    # 1. Train first model (linear regression)
    train_payload1 = {
        "datasetId": uploaded_dataset["_id"],
        "targetColumn": "Salary",
        "features": ["Age"],
        "algorithm": "linear_regression",
        "hyperparameters": {},
        "splitRatio": 0.2,
        "randomState": 42
    }
    res1 = await client.post(
        f"/api/projects/{project_id}/models/train",
        json=train_payload1,
        headers=auth_header
    )
    assert res1.status_code == 201
    model1_id = res1.json()["_id"]

    # 2. Train second model (ridge regression)
    train_payload2 = {
        "datasetId": uploaded_dataset["_id"],
        "targetColumn": "Salary",
        "features": ["Age"],
        "algorithm": "ridge",
        "hyperparameters": {"alpha": 1.0},
        "splitRatio": 0.2,
        "randomState": 42
    }
    res2 = await client.post(
        f"/api/projects/{project_id}/models/train",
        json=train_payload2,
        headers=auth_header
    )
    assert res2.status_code == 201
    model2_id = res2.json()["_id"]

    # 3. Compare models in the workspace
    compare_res = await client.get(
        f"/api/projects/{project_id}/models/compare",
        headers=auth_header
    )
    assert compare_res.status_code == 200
    compare_data = compare_res.json()
    assert len(compare_data["comparisonTable"]) >= 2
    assert compare_data["bestModelId"] in [model1_id, model2_id]
    assert "recommendationReason" in compare_data

    # 4. List all models
    list_res = await client.get(
        f"/api/projects/{project_id}/models",
        headers=auth_header
    )
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 2

    # 5. Delete model1
    del_res = await client.delete(
        f"/api/projects/{project_id}/models/{model1_id}",
        headers=auth_header
    )
    assert del_res.status_code == 200
    assert del_res.json()["message"] == "Model deleted successfully"

    # Verify model1 is deleted
    get_res = await client.get(
        f"/api/projects/{project_id}/models/{model1_id}",
        headers=auth_header
    )
    assert get_res.status_code == 404
