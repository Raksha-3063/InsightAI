import pytest

@pytest.mark.asyncio
async def test_register_user_success(client):
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    }
    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["name"] == user_data["name"]
    assert json_data["email"] == user_data["email"]
    assert "password" not in json_data
    assert "_id" in json_data

@pytest.mark.asyncio
async def test_register_user_duplicate_email(client):
    user_data = {
        "name": "Another User",
        "email": "test@example.com",
        "password": "password123"
    }
    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_login_user_success(client):
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_user_invalid_credentials(client):
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

@pytest.mark.asyncio
async def test_get_profile_success(client):
    # Log in first
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    login_resp = await client.post("/api/auth/login", json=login_data)
    token = login_resp.json()["access_token"]
    
    # Request profile
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/auth/profile", headers=headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["email"] == "test@example.com"
    assert json_data["name"] == "Test User"

@pytest.mark.asyncio
async def test_get_profile_unauthorized(client):
    response = await client.get("/api/auth/profile")
    assert response.status_code == 401
