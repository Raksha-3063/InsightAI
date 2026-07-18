# Codebase Concerns

**Analysis Date:** 2026-07-18

## Tech Debt

**Linting Failures in React App Router:**
- Issue: Severe ESLint rules violations preventing successful Next.js builds.
- Files:
  - `frontend/src/app/dashboard/page.tsx`
  - `frontend/src/app/login/page.tsx`
  - `frontend/src/app/register/page.tsx`
- Why: Rapid prototyping without running builds or pre-commit hooks.
- Impact: Next.js production builds (`npm run build`) will fail. The specific issues are:
  - Accessing variables before declaration: `fetchProjects` and `fetchDataset` are called inside `useEffect` on mount but are declared as const arrow functions *below* the hooks.
  - Calling `setState` synchronously within a `useEffect` hook (`setDataset(null)` inside the `activeProject` observer).
  - Implicit use of `any` types for caught exceptions (`catch (err: any)`).
- Fix approach:
  - Move const arrow functions above `useEffect` hooks in `page.tsx` (or declare them as traditional hoisted `async function` declarations).
  - Avoid synchronous state-setting in `useEffect` when conditional renders or initial states can suffice.
  - Define custom TypeScript error interfaces or use type assertions instead of `any`.

**Deprecated API usages in Backend:**
- Issue: Several warning-level deprecations raised by newer library versions.
- Files:
  - `backend/app/auth/routes.py`
  - `backend/app/routes/project.py`
  - `backend/app/routes/dataset.py`
  - `backend/app/services/parser.py`
  - `backend/tests/conftest.py`
- Why: Python 3.12 and newer package suites deprecate older UTC syntax and shortcuts.
- Impact: Future dependency upgrades will fail or cause runtime crashes.
  - `datetime.utcnow()` is deprecated. Python 3.12 warning: Use `datetime.now(datetime.UTC)` instead.
  - `pd.to_datetime(..., errors='ignore')` in Pandas 2.2 is deprecated.
  - Pytest event loop fixture redefinition in `conftest.py` is deprecated.
  - HTTPX client construction: `AsyncClient(app=app)` is deprecated in favor of `transport=ASGITransport(app=app)`.
- Fix approach: Update backend datetime and dependency invocations to modern versions.

## Known Bugs

- None currently active in core functionality (all 11 backend API tests pass).

## Security Considerations

**Hardcoded Secrets Fallback:**
- Risk: `JWT_SECRET` is hardcoded as `"supersecretjwtkeyinsightai2026!!!"` in `backend/app/config.py`. If a developer forgets to set a `.env` variable in production, the application will fallback to a public security token.
- File: `backend/app/config.py` (Line 7).
- Current mitigation: None in code.
- Recommendations: Set settings default to `None` or raise a ConfigurationError on startup if `JWT_SECRET` is not set in production.

**Unrestricted File Size Upload:**
- Risk: Backend does not limit file size. Users could upload 5GB CSV files, exhausting local disk space or causing a Python MemoryError during Pandas parsing.
- File: `backend/app/routes/dataset.py`.
- Current mitigation: Basic file extension validation only.
- Recommendations: Read the file headers/size beforehand or use a middleware constraint on the request body size.

## Performance Bottlenecks

**Memory exhaustion on Large Files:**
- Problem: `pd.read_csv` and `pd.read_excel` load the entire dataset into memory to parse row and column counts.
- File: `backend/app/services/parser.py`.
- Measurement: 100MB+ datasets could exceed local RAM boundaries on low-cost servers.
- Cause: Eager loading of tables.
- Improvement path: Parse in chunks (`chunksize`) or use stream parsers like `csv.reader` to extract metadata without fully loading dataframes.

## Fragile Areas

**Local uploads directory cleanup:**
- File: `backend/app/uploads/`.
- Why fragile: Uploaded datasets are written to local disk. If projects or datasets are deleted, the raw files remain on disk indefinitely, leading to storage leaks.
- Test coverage: No test exercises filesystem cleanup on database removals.
- Safe modification: Build a cleanup background task or implement file deletion when a dataset document is deleted.

## Scaling Limits

**Local File Storage:**
- Current capacity: Limited by the server's local hard drive storage.
- Limit: Hard disk capacity.
- Scaling path: Migrate to S3, Google Cloud Storage, or Cloudinary.

## Test Coverage Gaps

**Frontend Verification:**
- What's not tested: The entire Next.js UI is untested. Any regression in components, layouts, or state updates will go undetected until manual smoke tests.
- Priority: High.
- Difficulty to test: Requires installing testing libraries (Playwright or Jest/React Testing Library) and setting up mock endpoints.

---

*Concerns audit: 2026-07-18*
*Update as issues are fixed or new ones discovered*
