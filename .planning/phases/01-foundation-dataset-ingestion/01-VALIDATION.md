---
phase: 1
slug: foundation-dataset-ingestion
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-08
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (backend), vitest (frontend) |
| **Config file** | backend/pytest.ini (created in Wave 0) |
| **Quick run command** | `pytest backend/tests/test_auth.py` |
| **Full suite command** | `pytest backend/tests/` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick run command
- **After every plan wave:** Run full suite command
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | AUTH-01 | — | Passwords hashed with bcrypt | unit | `pytest backend/tests/test_auth.py` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | AUTH-02 | — | JWT token signatures verified | unit | `pytest backend/tests/test_auth.py` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 2 | PROJ-01 | — | User isolates projects | unit | `pytest backend/tests/test_projects.py` | ❌ W0 | ⬜ pending |
| 01-02-02 | 02 | 2 | DATA-01 | — | Restrict size & types on upload | unit | `pytest backend/tests/test_upload.py` | ❌ W0 | ⬜ pending |
| 01-02-03 | 02 | 2 | DATA-03 | — | CSV/Excel metadata parsed | unit | `pytest backend/tests/test_upload.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/conftest.py` — setup mongodb mock or test database client
- [ ] `backend/tests/test_auth.py` — test cases for registration and login
- [ ] `backend/tests/test_projects.py` — test cases for project creation
- [ ] `backend/tests/test_upload.py` — test cases for file parsing and metadata validation

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Frontend dashboard loading | PROJ-02 | UI verification | Start frontend and view dashboard at `http://localhost:3000` |
| Uploader drag-and-drop | DATA-01 | Drag-and-drop events | Drop a CSV file on the uploader box, verify upload status |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** {pending / approved 2026-07-08}
