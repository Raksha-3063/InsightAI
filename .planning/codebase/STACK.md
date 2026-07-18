# Technology Stack

**Analysis Date:** 2026-07-18

## Languages

**Primary:**
- Python 3.12.6 - Backend application logic, data parsing, database connection, and testing.
- TypeScript 5.x - Frontend React components, contexts, and API services.

**Secondary:**
- JavaScript / ESM - Frontend config files (`next.config.ts`, `postcss.config.mjs`, `eslint.config.mjs`).
- HTML/CSS - Global styles (`globals.css`) and basic structure.

## Runtime

**Environment:**
- Python 3.12.6 Interpreter - Backend runtime.
- Node.js 20.x or higher - Frontend build and development server runtime.

**Package Manager:**
- pip - Python packages managed via `backend/requirements.txt`.
- npm 10.x - Frontend packages managed via `frontend/package.json` and `frontend/package-lock.json`.

## Frameworks

**Core:**
- FastAPI 0.111.0 - Backend REST API framework with Swagger/OpenAPI support and lifespan event hooks.
- Next.js 16.2.10 (React 19.2.4) - Frontend framework with App Router, SSR, and client-side components.

**Testing:**
- pytest 8.2.2 - Backend unit and integration test runner.
- pytest-asyncio 0.23.7 - Async test support for pytest.

**Build/Dev:**
- Tailwind CSS 4.x - Modern utility-first styling framework with CSS-first configuration.
- PostCSS 8.x - Used for CSS compiling/processing.
- TypeScript compiler - Static type checking for frontend code.

## Key Dependencies

**Critical:**
- motor 3.4.0 - Asynchronous Python driver for MongoDB.
- pandas 2.2.2 - Data analysis and manipulation library used for dataset processing and metadata extraction.
- openpyxl 3.1.5 - Excel file reading engine for Pandas.
- PyJWT 2.8.0 - JWT (JSON Web Token) encoding and decoding for user authentication.
- passlib 1.7.4 - Password hashing utility using bcrypt.
- axios 1.18.1 - Promise-based HTTP client for the browser used to communicate with the FastAPI backend.
- lucide-react 1.23.0 - Icon library for the React UI.

**Infrastructure:**
- uvicorn 0.30.1 - ASGI server implementation for running the FastAPI application.
- pydantic 2.7.4 - Data validation and settings management using Python type annotations.
- pydantic-settings 2.3.4 - Settings management using environment variables.
- httpx 0.27.0 - Next-generation HTTP client for Python, used for async testing.

## Configuration

**Environment:**
- Backend: Configured using a `.env` file containing database connections, secrets, and directories, which is read by Pydantic's `BaseSettings` (`backend/app/config.py`).
- Frontend: Configured using environment variables like `NEXT_PUBLIC_API_URL` to point to the backend server (`frontend/src/services/api.ts`).

**Build:**
- `frontend/tsconfig.json` - TypeScript compilation settings.
- `frontend/next.config.ts` - Next.js custom configuration.
- `frontend/postcss.config.mjs` - Tailwind PostCSS integration.

## Platform Requirements

**Development:**
- Windows/macOS/Linux with Python 3.12+ and Node.js 20+.
- Local MongoDB instance or MongoDB Atlas cloud cluster for testing and database queries.

**Production:**
- Backend: ASGI-compatible server host (Render, Railway, AWS ECS, or Docker container).
- Frontend: Static/serverless deployment target (Vercel, Netlify).
- Database: MongoDB Atlas managed cluster.

---

*Stack analysis: 2026-07-18*
*Update after major dependency changes*
