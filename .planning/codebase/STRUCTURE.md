# Codebase Structure

**Analysis Date:** 2026-07-18

## Directory Layout

```
Insight AI/
├── .agents/                    # Custom agent configuration and skill resources
│   ├── gsd-core/              # Core GSD scripts and workflows
│   └── skills/                # Specialized project skills
├── .planning/                  # Project roadmap, state, requirements, and codebase mapping
│   ├── codebase/              # Codebase maps (STACK.md, STRUCTURE.md, etc.)
│   └── phases/                # Phase plans and research documents
├── backend/                    # Python FastAPI Backend codebase
│   ├── app/                   # Backend application source
│   │   ├── auth/              # Auth route handlers and service logic
│   │   ├── database/          # Database connection manager
│   │   ├── models/            # Database representation models (User, Project, Dataset)
│   │   ├── routes/            # Router blueprints (project.py, dataset.py)
│   │   ├── schemas/           # Pydantic serialization/deserialization schemas
│   │   ├── services/          # Pandas data parser and analytical utilities
│   │   ├── uploads/           # Local directory for uploaded files (gitignored)
│   │   ├── config.py          # Pydantic settings loading from .env
│   │   └── main.py            # Main app startup and router registration
│   ├── tests/                 # Backend test suite (using Pytest)
│   └── requirements.txt       # Backend dependencies manifest
└── frontend/                   # TypeScript Next.js Frontend codebase
    ├── src/                   # Frontend React source code
    │   ├── app/               # Next.js App Router folders and styles
    │   │   ├── dashboard/     # Workspace dashboard page file
    │   │   ├── login/         # User login screen page file
    │   │   ├── register/      # User registration screen page file
    │   │   ├── globals.css    # Global Tailwind styles
    │   │   ├── layout.tsx     # Base App HTML structure
    │   │   └── page.tsx       # Public home page
    │   ├── contexts/          # Session authentication React Context
    │   └── services/          # Axios instance and response interceptors
    ├── package.json           # Frontend dependencies and npm scripts
    └── tsconfig.json          # TypeScript compilation configuration
```

## Directory Purposes

**backend/app/auth/**
- Purpose: Handles register, login, profile authentication logic.
- Key files: `routes.py` (auth routing endpoints), `service.py` (password hashing and token signing helpers).

**backend/app/routes/**
- Purpose: Endpoint handlers for workspaces and datasets.
- Key files: `project.py` (workspace project CRUD), `dataset.py` (CSV/Excel upload, database ingestion, schema retrieval).

**backend/app/services/**
- Purpose: Service operations.
- Key files: `parser.py` (Pandas file reader, row/column counter, null/duplicate count, type classifier).

**backend/app/uploads/**
- Purpose: Stores raw user CSV/Excel files locally.
- Note: Gitignored except for `.gitkeep`.

**frontend/src/app/**
- Purpose: Frontend Next.js routing and UI component page views.
- Key files: `dashboard/page.tsx` (main analytics dashboard, modal dialogs, file upload area, schemas table).

**frontend/src/contexts/**
- Purpose: Exposes global authentication state.
- Key files: `AuthContext.tsx` (manages API tokens, sign in, sign out, user storage).

## Key File Locations

**Entry Points:**
- `backend/app/main.py` - Backend server startup entry.
- `frontend/src/app/page.tsx` - Frontend landing page.

**Configuration:**
- `backend/app/config.py` - Backend configuration schema.
- `frontend/next.config.ts` - Next.js config settings.
- `frontend/src/services/api.ts` - Axios client setup.

**Core Logic:**
- `backend/app/services/parser.py` - Dataset parsing and metadata analysis.

**Testing:**
- `backend/tests/` - Backend test collection.
- `backend/tests/conftest.py` - Shared Pytest test database setup fixtures.

## Naming Conventions

**Files:**
- Backend: Snake case for all filenames (`connection.py`, `test_auth.py`).
- Frontend: PascalCase for components/contexts (`AuthContext.tsx`), camelCase for utility modules (`api.ts`).

**Directories:**
- Backend: Snake case (`app`, `database`, `uploads`).
- Frontend: Lowercase or kebab-case (`src`, `contexts`, `dashboard`).

**Variables and Functions:**
- Backend: Snake case (`get_current_user`, `verify_password`).
- Frontend: Camel case (`handleFileUpload`, `fetchProjects`).

## Where to Add New Code

**New Data Cleaning / Analytics Module:**
- Service Logic: Add files in `backend/app/services/` (e.g. `cleaner.py`).
- Route Handlers: Expose REST endpoints in `backend/app/routes/dataset.py`.
- Tests: Add integration/unit tests in `backend/tests/test_dataset.py` or new files.

**New Interactive Visualization / Visual Component:**
- Implementation: Create a components folder `frontend/src/components/` and import inside `frontend/src/app/dashboard/page.tsx`.

---

*Structure analysis: 2026-07-18*
*Update when directory structure changes*
