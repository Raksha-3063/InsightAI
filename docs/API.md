# REST API Documentation: InsightAI

InsightAI exposes a modular, documented JSON REST API. Automatic interactive documentation is available at `/docs` (Swagger UI).

---

## Authentication Endpoints

### `POST /api/auth/register`
Registers a new user account.
* **Request Body**: `{"name": "string", "email": "user@example.com", "password": "password123"}`
* **Response**: `{"_id": "string", "name": "string", "email": "string", "createdAt": "ISOString"}`

### `POST /api/auth/login`
Logs in and generates JWT access/refresh tokens.
* **Request Body**: `{"email": "user@example.com", "password": "password123"}`
* **Response**: `{"access_token": "string", "refresh_token": "string", "token_type": "bearer"}`

### `POST /api/auth/refresh`
Generates a new access token using a refresh token.
* **Request Body**: `{"refresh_token": "string"}`
* **Response**: `{"access_token": "string", "refresh_token": "string", "token_type": "bearer"}`

---

## Project & Dataset Management

### `POST /api/projects`
Creates a new BI workspace.
* **Headers**: `Authorization: Bearer <access_token>`
* **Response**: `{"_id": "string", "projectName": "string", "description": "string", "createdDate": "ISOString"}`

### `POST /api/projects/{projectId}/datasets/upload`
Uploads a new CSV or Excel dataset.
* **Payload**: Multipart file upload. Limit is 50MB.
* **Response**: Ingested schema metadata including health score, column types, correlation coefficients, and statistical summaries.

---

## Model Training & Forecasting

### `POST /api/projects/{projectId}/models/train`
Triggers ML pipeline training.
* **Request Body**: `{"datasetId": "string", "targetColumn": "string", "features": ["string"], "algorithm": "random_forest", "hyperparameters": {}, "splitRatio": 0.2}`
* **Response**: Model metadata including unique ID, status (`"pending"` or `"completed"`), hyperparams, and metrics.

### `POST /api/projects/{projectId}/forecast/train`
Triggers forecasting pipeline training.
* **Request Body**: `{"datasetId": "string", "dateColumn": "string", "targetColumn": "string", "algorithm": "arima", "horizon": 30}`
* **Response**: Forecasting job metadata.

### `GET /api/projects/{projectId}/models/{mlModelId}/explanations`
Computes SHAP and LIME details for a specific model.
* **Query Parameters**: `rowIndex=0`

---

## AI Copilot Endpoints

### `POST /api/projects/{projectId}/ai/chat`
Performs conversational data analysis.
* **Request Body**: `{"message": "string", "datasetId": "string", "conversationId": "string"}`

### `POST /api/projects/{projectId}/ai/report`
Generates publication-quality executive reports.
* **Request Body**: `{"datasetId": "string", "format": "markdown"}`

---

## Background Worker Jobs

### `GET /api/projects/{projectId}/jobs/{jobId}`
Queries the execution status of a Celery background task.
* **Response**: `{"_id": "string", "status": "pending|running|completed|failed", "jobType": "string", "result": {}, "error": "string"}`
