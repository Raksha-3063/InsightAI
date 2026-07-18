# Coding Conventions

**Analysis Date:** 2026-07-18

## Naming Patterns

**Files:**
- Backend: Snake case for all Python modules (`main.py`, `connection.py`, `parser.py`).
- Frontend Next.js: Lowcase/kebab-case for folder routes (`dashboard`, `login`, `register`); page components use `page.tsx`. Contexts use PascalCase (`AuthContext.tsx`).

**Functions:**
- Backend: Snake case (`get_current_user`, `verify_password`, `parse_file_metadata`).
- Frontend: Camel case (`handleFileUpload`, `fetchProjects`, `logout`).

**Classes:**
- Backend: PascalCase (`Database`, `Settings`, `UserResponse`, `DatasetResponse`).

**Variables:**
- Backend: Snake case for standard variables, UPPER_SNAKE_CASE for constants (`ACCESS_TOKEN_EXPIRE_MINUTES`, `UPLOAD_DIR`).
- Frontend: Camel case for normal variables, PascalCase for component/state representations.

## Code Style

**Formatting:**
- Backend: Standard Python styling (PEP 8) with explicit type hints.
- Frontend: TypeScript style, 2 space indentation, single quotes for strings, semicolons required. Tailwind v4 styling with responsive design markers.

**Linting:**
- Frontend: ESLint with Next.js configurations (`next/core-web-vitals`).
- Backend: Basic syntax and Pytest verification.

## Import Organization

**Backend Order:**
1. Standard library imports (`os`, `asyncio`, `datetime`).
2. Third-party package imports (`fastapi`, `pydantic`, `motor`, `pandas`).
3. Local application imports (`from backend.app.database.connection import ...`).

**Frontend Order:**
1. React core hooks (`useState`, `useEffect`, `useRef`).
2. Next.js router utilities (`useRouter`, `usePathname`).
3. Context hooks (`useAuth`).
4. API service client (`api`).
5. Icon library components (`lucide-react`).

## Error Handling

**Backend Patterns:**
- Route endpoints raise `HTTPException` with specific HTTP status codes (400, 401, 404, 422, 500) and descriptive detail payloads.
- Background parses are wrapped in try-except blocks to catch CSV/Excel parsing errors, cleaning up files from disk before throwing unprocessable entity errors.

**Frontend Patterns:**
- Try/catch blocks in UI handlers catch API errors and extract the backend payload (`err.response?.data?.detail`).
- Response interceptors in `frontend/src/services/api.ts` catch 401 status responses and automatically remove tokens from storage to force a clean logout state.

## Logging

- Backend: Basic terminal log prints on startup/shutdown event loops.
- Frontend: Standard `console.error` and `console.log` for debugging and logging client failures.

---

*Convention analysis: 2026-07-18*
*Update when patterns change*
