# Phase 1: Foundation & Dataset Ingestion - Context

**Gathered:** 2026-07-08
**Status:** Ready for planning
**Source:** PRD (User Request)

<domain>
## Phase Boundary

This phase establishes the project structure, sets up user authentication and database models, enables project isolation, and implements CSV/Excel dataset uploads with automatic metadata extraction.

</domain>

<decisions>
## Implementation Decisions

### Technology Stack & Architecture
- FastAPI (Python) for the backend REST APIs.
- Next.js (React/TypeScript) for the frontend dashboard.
- MongoDB Atlas as the primary database.
- Local filesystem storage (`backend/app/uploads/`) for dataset storage in development.
- JWT authentication for session management.

### Database Schema Design

#### Users Collection
- `_id` (ObjectId)
- `name` (string)
- `email` (string, unique)
- `password` (string, hashed)
- `createdAt` (datetime)

#### Projects Collection
- `_id` (ObjectId)
- `userId` (ObjectId, references Users)
- `projectName` (string)
- `description` (string)
- `createdAt` (datetime)

#### Dataset Collection
- `_id` (ObjectId)
- `projectId` (ObjectId, references Projects)
- `fileName` (string)
- `rows` (integer)
- `columns` (integer)
- `missingValues` (integer)
- `duplicateRows` (integer)
- `size` (integer)
- `uploadDate` (datetime)

### Ingestion & Validation
- Formats: CSV and Excel (`.xlsx`).
- Upon upload, the backend automatically calculates and stores:
  - Total row and column count.
  - Data type of each column.
  - Total number of missing values and duplicate rows.
  - File size and memory usage.
  - Lists of numerical vs categorical vs date columns.

### the agent's Discretion
- Code structure and API endpoint paths (standard REST conventions).
- React folder structures (components, services, hooks, types).
- Specific UI layout of login and project upload cards.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Project context and vision.
- `.planning/REQUIREMENTS.md` — Complete product requirements list.

</canonical_refs>

<specifics>
## Specific Ideas

- The dashboard should show Quick Actions, Dataset Statistics, Recent Reports, and Recent Models.

</specifics>

<deferred>
## Deferred Ideas

- Google OAuth, Email verification, JSON/SQL/Google Sheets import (deferred to v2 / Phase 5).

</deferred>

---
*Phase: 01-foundation-dataset-ingestion*
*Context gathered: 2026-07-08 from user PRD*
