# Phase 1: Foundation & Dataset Ingestion - Research

**Researched:** 2026-07-08
**Domain:** FastAPI, Next.js, JWT, MongoDB Atlas, File Upload & Parsing
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- FastAPI (Python) for the backend REST APIs.
- Next.js (React/TypeScript) for the frontend dashboard.
- MongoDB Atlas as the primary database.
- Local filesystem storage (`backend/app/uploads/`) for dataset storage in development.
- JWT authentication for session management.
- Database schemas for Users, Projects, Datasets.
- Upload formats: CSV and Excel (.xlsx).
- Automated dataset metadata parsing (rows, columns, missing values, duplicate count, types, memory usage).

### the agent's Discretion
- Code structure and API endpoint paths.
- React folder structures (components, services, hooks, types).
- Specific UI layout of login and project upload cards.

### Deferred Ideas (OUT OF SCOPE)
- Google OAuth, Email verification, JSON/SQL/Google Sheets import (deferred to v2 / Phase 5).

</user_constraints>

<architectural_responsibility_map>
## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| User Register/Login APIs | API/Backend | Database/Storage | Handled by FastAPI auth routes, stored in MongoDB |
| JWT Token Generation & Verification | API/Backend | — | Cryptographic token handling in backend middleware |
| Project Creation & Listing APIs | API/Backend | Database/Storage | Project metadata CRUD in backend and MongoDB |
| Dataset File Upload | API/Backend | Local Storage | API accepts files, saves them to local disk |
| Metadata Extraction & Validation | API/Backend | — | Processed in Python memory via Pandas |
| Dashboard UI & Navigation | Browser/Client | — | Next.js App Router renders pages, Axios queries APIs |

</architectural_responsibility_map>

<research_summary>
## Summary

This phase establishes the foundational stack for InsightAI. We will use FastAPI with motor (async MongoDB driver) and Pydantic v2. This setup provides rapid, type-safe API endpoints with automatic Swagger documentation.

For authentication, we will use PyJWT for token signatures and passlib[bcrypt] for password hashing. Dataset parsing will utilize Pandas for high-performance tabular data inspection, and openpyxl as the backend engine for Excel parsing.

**Primary recommendation:** Use FastAPI's APIRouter structure with a clean separation of models, schemas, and routes, and set up a robust, reusable async MongoDB helper class.

</research_summary>

<standard_stack>
## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| fastapi | 0.111.0 | Backend API framework | Fast, modern, async-first, automatic Swagger |
| uvicorn | 0.30.1 | ASGI web server | High-performance ASGI server for Python |
| motor | 3.4.0 | Async MongoDB driver | Standard async wrapper for PyMongo |
| pydantic | 2.7.4 | Data validation | Native type-safety and schemas for FastAPI |
| PyJWT | 2.8.0 | JWT generation/decoding | Standard library for signing/verifying JWTs |
| passlib[bcrypt] | 1.7.4 | Password hashing | Secure bcrypt hashing for passwords |
| pandas | 2.2.2 | Data analysis & parsing | Fast tabular parsing of CSVs/Excels |
| openpyxl | 3.1.5 | Excel parsing engine | Standard engine for reading modern .xlsx in Pandas |

### Supporting (Frontend)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| next | 14.2.4 | React application framework | Standard frontend App Router architecture |
| axios | 1.7.2 | HTTP client | Communicating with the FastAPI backend |
| tailwindcss | 3.4.4 | Styling | Rapid utility-first CSS styling |
| lucide-react | 0.395.0 | Icons | Dashboard and UI iconography |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| motor | pymongo | PyMongo is synchronous, which blocks FastAPI's event loop; motor keeps queries non-blocking. |
| PyJWT | python-jose | PyJWT is actively maintained and has fewer cryptography dependency quirks. |
| local filesystem | S3/Cloudinary | Cloud storage is deferred to Phase 5 production deployment to keep the MVP simple. |

**Installation (Backend):**
```bash
pip install fastapi uvicorn motor pydantic[email] PyJWT passlib[bcrypt] pandas openpyxl python-multipart
```
</standard_stack>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Password Hashing | Custom hashing/salt | passlib[bcrypt] | Hand-rolled hashing lacks protection against modern GPU-based brute-force attacks |
| JWT Verification | Custom header decoding | PyJWT | Crypto verification requires strict signature/header checks to prevent spoofing |
| File Parsing | Custom CSV text parsing | Pandas | Pandan handles edge cases like escape characters, line endings, and delimiter detection |
| DB Connection Pool | Custom MongoClient management | Motor Client | Motor maintains a built-in connection pool and manages timeouts automatically |

</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Synchronous Database/File Calls
**What goes wrong:** FastAPI performance drops, API becomes unresponsive under load.
**Why it happens:** Blocking code (e.g. `open().read()` or synchronous MongoDB queries) blocks the single-threaded event loop.
**How to avoid:** Use `motor` for database queries and run heavy file-read parsing (Pandas) in an async thread pool using FastAPI's `run_in_threadpool`.

### Pitfall 2: Out of Memory on Large File Uploads
**What goes wrong:** Server crashes or runs out of RAM when a user uploads a large CSV file.
**Why it happens:** Reading the entire file into memory as a Pandas DataFrame at once consumes excessive memory.
**How to avoid:** Read file headers and structure first. Limit file uploads to a max size (e.g., 50MB) and parse statistics using memory-efficient chunking if needed.

### Pitfall 3: JWT Key Exposure
**What goes wrong:** Secret key is leaked, allowing anyone to sign their own admin JWTs.
**Why it happens:** Storing SECRET_KEY in source code instead of environment variables.
**How to avoid:** Load keys from env vars using Pydantic Settings.

</common_pitfalls>

<code_examples>
## Code Examples

### FastAPI Async MongoDB Setup
```python
from motor.motor_asyncio import AsyncIOMotorClient
import os

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_helper = Database()

async def connect_to_mongo():
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DATABASE_NAME", "insightai")
    db_helper.client = AsyncIOMotorClient(mongo_url)
    db_helper.db = db_helper.client[db_name]

async def close_mongo_connection():
    db_helper.client.close()
```

### Pandas Metadata Extraction
```python
import pandas as pd

def extract_dataset_metadata(file_path: str):
    # For CSV, read first few rows to confirm it is valid, then load stats
    df = pd.read_csv(file_path)
    
    metadata = {
        "rows": len(df),
        "columns": len(df.columns),
        "missingValues": int(df.isnull().sum().sum()),
        "duplicateRows": int(df.duplicated().sum()),
        "size": os.path.getsize(file_path),
        "column_info": {col: str(dtype) for col, dtype in df.dtypes.items()}
    }
    return metadata
```

</code_examples>

<sources>
## Sources

### Primary (HIGH confidence)
- FastAPI Docs (fastapi.tiangolo.com) - APIRouter and OAuth2 Password Bearer.
- Motor Docs (motor.readthedocs.io) - Async motor client patterns.
- Pandas Docs (pandas.pydata.org) - DataFrame statistics and read_csv/read_excel.

</sources>

<metadata>
## Metadata

**Research scope:**
- Core technology: FastAPI, Next.js, MongoDB Atlas
- Ecosystem: motor, PyJWT, passlib, Pandas
- Patterns: Async database helpers, metadata parser, JWT auth middleware
- Pitfalls: Blocking event loops, large upload memory exhaustion

**Confidence breakdown:**
- Standard stack: HIGH - standard, stable production python libraries
- Architecture: HIGH - REST standard patterns
- Pitfalls: HIGH - standard async issues
- Code examples: HIGH - official library docs

**Research date:** 2026-07-08
**Valid until:** 2026-08-08
</metadata>

---
*Phase: 01-foundation-dataset-ingestion*
*Research completed: 2026-07-08*
*Ready for planning: yes*
