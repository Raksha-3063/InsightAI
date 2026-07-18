# Testing Patterns

**Analysis Date:** 2026-07-18

## Test Framework

**Runner:**
- Pytest 8.2.2 (Backend tests).
- Configured with `pytest-asyncio` for asynchronous test methods.

**Assertion Library:**
- Standard Python `assert` statements.

**Run Commands:**
- Run all backend tests:
  ```powershell
  # Windows PowerShell
  $env:PYTHONPATH="."; pytest
  ```
  ```bash
  # Linux/macOS
  PYTHONPATH=. pytest
  ```

## Test File Organization

**Location:**
- Backend: `backend/tests/`.
- Frontend: No automated test suite set up yet.

**Naming:**
- `test_*.py` pattern for all backend tests:
  - `test_auth.py` for user registration and JWT verification.
  - `test_projects.py` for workspace CRUD APIs.
  - `test_dataset.py` for CSV/Excel file validation, uploads, and schema parsing.

**Structure:**
```
backend/
  tests/
    conftest.py             # Shared fixtures & test database setup
    test_auth.py            # User Auth test cases
    test_projects.py        # Workspace Project test cases
    test_dataset.py         # File ingestion test cases
```

## Test Structure

**Suite Organization:**
```python
import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_feature_success(client: AsyncClient):
    # Arrange: Setup request data
    payload = {"key": "value"}
    
    # Act: Send HTTP request
    response = await client.post("/api/feature", json=payload)
    
    # Assert: Verify response and codes
    assert response.status_code == 201
    assert response.json()["status"] == "ok"
```

**Setup & Teardown:**
- Fixtures are declared in `backend/tests/conftest.py`.
- `test_db_setup`: Redefines the `settings.DATABASE_NAME` to `insightai_test`, triggers `connect_to_mongo()`, clears the test database collections, yields, and then teardown runs collection cleanups and closes connection.
- `client`: Yields an `httpx.AsyncClient` pointing to the active FastAPI app.

## Mocking

- Database calls: No mock wrappers used. Tests connect to a real local MongoDB test instance (`insightai_test`) for end-to-end integration tests.
- File system: Upload files are created on-the-fly and written to the actual development uploads folder, then cleaned up.

## Test Types

- Integration / End-to-End API Tests: Backend routes are fully exercised via `httpx.AsyncClient` from the requests down to database insertions.

---

*Testing analysis: 2026-07-18*
*Update when test patterns change*
