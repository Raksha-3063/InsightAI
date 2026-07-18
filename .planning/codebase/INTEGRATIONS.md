# External Integrations

**Analysis Date:** 2026-07-18

## APIs & External Services

**AI Engine (Planned for Phase 4):**
- Gemini API - Used for AI-powered data insights, explainable AI explanations, and natural language chatbot.
  - SDK/Client: google-generativeai python package (or REST API calls via httpx)
  - Auth: API key passed in environment variable (e.g. `GEMINI_API_KEY`)

## Data Storage

**Databases:**
- MongoDB Atlas / Local MongoDB - Primary data store for storing users, projects, and dataset metadata.
  - Connection: Connection string configured via `MONGODB_URL` env var.
  - Client: Motor (`motor.motor_asyncio.AsyncIOMotorClient`) - Asynchronous Python driver for MongoDB.
  - Collections:
    - `users`: User credentials and profiles.
    - `projects`: Isolated workspaces belonging to users.
    - `datasets`: Metadata and statistics of uploaded CSV/Excel files.

**File Storage:**
- Local Filesystem Storage - Stores the uploaded original CSV/Excel files in `backend/app/uploads/` during development.
  - Connection: Local directory path configured in settings (`UPLOAD_DIR`).
  - Naming Pattern: `<projectId>_<timestamp>_<original_filename>` to prevent file name collisions.
- Cloud Storage (Planned for production/Phase 5):
  - Cloudinary, S3, or GCS for production file hosting.

## Authentication & Identity

**Auth Provider:**
- Custom JWT (JSON Web Tokens) Authentication.
  - Implementation: Python `jose` / `PyJWT` for encoding and decoding tokens; `passlib` with bcrypt for password hashing.
  - Token Storage: Local storage (`localStorage`) on the client side (`frontend/src/contexts/AuthContext.tsx`).
  - Authorization Header: `Bearer <token>` passed automatically via Axios interceptor on the client side.

## Monitoring & Observability

- Log output is directed to stdout/stderr. Standard python logger in development.

## CI/CD & Deployment

- None currently configured. (Planned to run on local dev server via `uvicorn` and `next dev`).

## Environment Configuration

**Development:**
- Required Env Vars (Backend):
  - `MONGODB_URL`: MongoDB connection URI (default: `mongodb://localhost:27017`)
  - `DATABASE_NAME`: Name of the database (default: `insightai`)
  - `JWT_SECRET`: Secret key for signing JWT tokens (default: `supersecretjwtkeyinsightai2026!!!`)
  - `ACCESS_TOKEN_EXPIRE_MINUTES`: Expiration time in minutes (default: `60`)
  - `UPLOAD_DIR`: Directory to store dataset uploads (default: `backend/app/uploads`)
- Required Env Vars (Frontend):
  - `NEXT_PUBLIC_API_URL`: Backend API URL (default: `http://localhost:8000/api`)

---

*Integration audit: 2026-07-18*
*Update when adding/removing external services*
