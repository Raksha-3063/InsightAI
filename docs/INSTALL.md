# Installation Guide: InsightAI

Follow this guide to set up and run InsightAI locally.

---

## Prerequisites

* **Python 3.12** or higher.
* **Node.js 20.x** (LTS) or higher.
* **MongoDB** (Local instance running at `mongodb://localhost:27017` or Atlas).
* **Redis** (Local instance running at `redis://localhost:6379` for Celery background tasks).

---

## 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create your local environment configuration:
   Copy `deployment/env.template` to `backend/.env` and fill in your variables (Gemini API key, database endpoints, etc.).

5. Start the FastAPI development gateway server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`. Swagger documentation is at `http://localhost:8000/docs`.

---

## 2. Start Background Workers (Optional)

If `CELERY_ENABLED` is set to `true` in your `.env`, start the Celery worker process:
```bash
cd backend
celery -A app.tasks.worker.celery_app worker --loglevel=info
```
Ensure Redis is running before starting the worker.

---

## 3. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install npm dependencies:
   ```bash
   npm install
   ```

3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:3000` in your browser.
