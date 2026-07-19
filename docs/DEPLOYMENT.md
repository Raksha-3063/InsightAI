# Deployment Guide: InsightAI

This guide details how to build and deploy InsightAI to production environments.

---

## 1. Docker Compose (Self-Hosted Production)

For self-hosting on single virtual machines (e.g. AWS EC2, DigitalOcean Droplet):

1. Clone the repository and configure `.env` variables.
2. Build and start production containers:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```
3. This spins up the Next.js frontend on port 3000, the FastAPI backend gateway on port 8000, and a Celery worker backed by Redis.

---

## 2. Cloud Platforms Deployment

### Database: MongoDB Atlas
1. Register a free tier shared cluster on MongoDB Atlas.
2. Go to Network Access and whitelist target server IPs (or allow `0.0.0.0/0` for generic connections).
3. Copy the cluster connection URI and replace `MONGODB_URL` in env parameters.

### Backend: Render or Railway
1. Link your GitHub repository.
2. Select **Web Service** on Render.
3. Configure settings:
   * **Environment**: `Python`
   * **Build Command**: `pip install -r backend/requirements.txt`
   * **Start Command**: `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`
4. Add all environment variables (e.g., `MONGODB_URL`, `JWT_SECRET`, `REDIS_URL`, `CELERY_ENABLED=true`, `GEMINI_API_KEY`).

### Background Workers: Render Private Service
1. Create a **Private Service** (not exposed to external traffic).
2. Start Command: `celery -A backend.app.tasks.worker.celery_app worker --loglevel=info`

### Frontend: Vercel
1. Select **New Project** and import the `frontend/` directory.
2. Configure environment variable:
   * `NEXT_PUBLIC_API_URL` = URL of your deployed Render backend (e.g. `https://insightai-backend.onrender.com/api`).
3. Click **Deploy**. Vercel will automatically build the Next.js production bundles and host them on CDN.
