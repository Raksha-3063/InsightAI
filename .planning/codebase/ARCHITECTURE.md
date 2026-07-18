# Architecture

**Analysis Date:** 2026-07-18

## Pattern Overview

**Overall:** Client-Server Monolithic API structure with a Next.js (React) frontend and a FastAPI (Python) backend using MongoDB as a persistent document store.

**Key Characteristics:**
- **Stateless request handling**: Requests contain a JWT token in the `Authorization` header to authenticate the user per request.
- **Asynchronous backend**: The backend leverages Python's `asyncio` and MongoDB's `motor` async driver for high performance.
- **Thread pool offloading**: CPU-intensive operations (like Pandas-based dataset parsing) are offloaded to a thread pool via FastAPI's `run_in_threadpool`.
- **Client-side session management**: User state is maintained on the client using React Context, persisted in `localStorage`.

## Layers

### Backend Layers

**API Routes (Controller/Endpoints) Layer:**
- Purpose: Exposes HTTP endpoints, parses incoming request models, handles request parameter validation, and handles HTTP exceptions.
- Locations: `backend/app/routes/project.py`, `backend/app/routes/dataset.py`, `backend/app/auth/routes.py`.
- Depends on: Service layer for business logic, schemas for data validation, database connection for direct DB query/mutation (in basic routes).
- Used by: External HTTP clients (e.g., Next.js frontend, Swagger UI).

**Service Layer:**
- Purpose: Implements business-specific logic, data parsing algorithms, and helper utilities.
- Locations: `backend/app/services/parser.py`, `backend/app/auth/service.py`.
- Depends on: Models and external packages (Pandas, PyJWT).
- Used by: API Routes layer.

**Database & Models Layer:**
- Purpose: Models represent the documents stored in MongoDB collections. Schemas handle serialization/deserialization validation.
- Locations: `backend/app/models/`, `backend/app/schemas/`, `backend/app/database/connection.py`.
- Depends on: Motor library, Pydantic settings.
- Used by: Service and API Routes layers.

### Frontend Layers

**UI Components & Pages Layer:**
- Purpose: Renders pages, forms, tables, and dashboards. Handles interactive user state (drag-and-drop, modals).
- Location: `frontend/src/app/`.
- Depends on: Auth Context and API Service.

**Auth Context (State Management):**
- Purpose: Coordinates authentication state, holds current logged-in user profile, and exposes login/logout/register functions.
- Location: `frontend/src/contexts/AuthContext.tsx`.
- Depends on: API Service.
- Used by: Pages and layouts to guard routes or display user profile information.

**API Service:**
- Purpose: Centralizes Axios configuration, base URL, headers, and request/response interceptors.
- Location: `frontend/src/services/api.ts`.
- Depends on: `axios` library.
- Used by: Auth Context and Pages to fetch data.

## Data Flow

### Dataset Ingestion Flow (End-to-End):

1. **User Action:** The user drops a CSV file in the drag-and-drop area of `frontend/src/app/dashboard/page.tsx`.
2. **Client Upload Request:** The page calls `handleFileUpload`, creating a `FormData` object containing the file, and submits a POST request to `/api/projects/{projectId}/datasets/upload` using Axios (`api.post`).
3. **Token Injection:** The Axios request interceptor in `frontend/src/services/api.ts` retrieves the JWT token from `localStorage` and appends it to the `Authorization` header.
4. **Backend Route Handler:** FastAPI intercepts the request. The route in `backend/app/routes/dataset.py` validates the project owner using `Depends(get_current_user)` (which queries MongoDB).
5. **File Verification & Disk Write:** The handler checks the file extension (.csv, .xlsx, .xls) and asynchronously writes the file stream to disk at `backend/app/uploads/` with a timestamp-prefixed filename.
6. **Thread Pool Processing:** To prevent blocking FastAPI's single-threaded async event loop, the handler calls `run_in_threadpool(parse_file_metadata, file_path, file_ext)`.
7. **Metadata Parsing:** The parser function in `backend/app/services/parser.py` loads the file using Pandas (`pd.read_csv` or `pd.read_excel`), calculates dataset stats (row/column counts, missing values, duplicates), and classifies column types.
8. **Database Write:** The handler inserts the metadata into the MongoDB `datasets` collection using the motor async client (`db_helper.db.datasets.insert_one`).
9. **JSON Response:** The route returns a 201 Created status and serializes the metadata payload into a `DatasetResponse` schema.
10. **Frontend Render:** The dashboard component receives the parsed metadata, saves it in the local React state (`setDataset`), and updates the UI to show the "Dataset Health Summary" and "Schema Columns" table.

## Key Abstractions

**Database Class (Singleton Helper):**
- Purpose: Manages the connection lifecycle of `AsyncIOMotorClient` and exposes the active database connection.
- Location: `backend/app/database/connection.py` (`db_helper` object).

**Pydantic Schemas / BaseModels:**
- Purpose: Define strict structures for request inputs and response outputs, allowing automatic JSON serialization and validation.
- Location: `backend/app/schemas/`.

## Entry Points

**FastAPI App Entry:**
- Location: `backend/app/main.py`.
- Triggers: Uvicorn execution (`uvicorn backend.app.main:app --reload`).
- Responsibilities: Registers routers, sets up CORS middlewares, and runs startup/shutdown lifespans (db connection setup).

**Next.js Page Entry:**
- Location: `frontend/src/app/page.tsx` (Root route).
- Triggers: Direct URL request to `/`.
- Responsibilities: Serves as the landing page, linking users to login or dashboard.

## Error Handling

**Backend Strategy:**
- Exceptions are caught locally at the router level and raised as `HTTPException` with specific status codes (400 Bad Request, 404 Not Found, 422 Unprocessable Entity, 500 Internal Server Error) and detail messages.
- The `lifespan` handles database connection issues.

**Frontend Strategy:**
- Axios interceptors catch 401 Unauthorized errors and automatically clear local storage.
- Page forms use try/catch blocks to intercept Axios errors, extracting the backend's error message (`err.response?.data?.detail`) and displaying it in an alert box.

## Cross-Cutting Concerns

**Authentication:**
- Decoupled from core route logic. Handled as a FastAPI dependency `Depends(get_current_user)` in route definitions to resolve the current active user from the JWT header.

**CORS Middleware:**
- Setup in `backend/app/main.py` allowing frontend domain origins to hit the backend APIs during local development.

---

*Architecture analysis: 2026-07-18*
*Update when major patterns change*
