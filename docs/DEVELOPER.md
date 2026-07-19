# Developer Guide: InsightAI

Welcome to the InsightAI codebase! This guide is for developers looking to modify, extend, or run tests on the platform.

---

## Coding Standards

### Backend (Python/FastAPI)
* Follow **PEP 8** formatting style.
* Keep routes light. All business, calculations, data profiling, machine learning fitting, and AI Copilot reasoning belong inside dedicated service classes.
* Always handle missing dependencies (like `mlflow` or `google.generativeai`) gracefully using mock fallbacks.

### Frontend (Next.js/TypeScript)
* Follow **ESLint** rules.
* Components should be responsive, accessible, and utilize curated Tailwind colors (avoid generic borders and text).
* Always handle loading states with custom animated loaders.

---

## Running the Test Suite

We use `pytest` for all backend testing. Bypassing rate limiting requires setting the `TESTING` environment variable to `"true"`.

### Run all tests
```bash
$env:PYTHONPATH="."; $env:TESTING="true"; pytest
```

### Run specific test files
```bash
pytest backend/tests/test_production.py
pytest backend/tests/test_ai.py
```

---

## Database Indexing

After database migrations or updates, run the index script to apply Mongo optimizations:
```bash
python scripts/setup_indexes.py
```
This script ensures lookup fields like `userId`, `projectId`, and `datasetId` have index mappings for rapid queries.
