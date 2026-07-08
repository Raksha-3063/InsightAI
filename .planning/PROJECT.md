# InsightAI

## What This Is

InsightAI is a modern, AI-powered Business Intelligence and data analytics platform. It allows users to upload datasets and automatically performs data cleaning, exploratory data analysis (EDA), visualization, machine learning, forecasting, explainable AI, and AI-powered business insights, eliminating the need to write Jupyter notebooks manually.

## Core Value

Eliminate the need for manual Jupyter notebook creation by providing a professional, automated analytics dashboard, predictive models, AI-generated reports, and an intelligent chatbot for uploaded data.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] **AUTH**: Register, Login, JWT Authentication, Forgot Password, and Profile.
- [ ] **PROJECT**: Create and manage projects (e.g., Retail Sales, Coffee Plantation) to store datasets, models, and reports separately.
- [ ] **UPLOAD**: Upload CSV/Excel datasets and store dataset metadata in MongoDB.
- [ ] **STORAGE**: Store original files in local storage (development) or cloud storage (production).
- [ ] **CLEAN**: Automatic data cleaning (replace missing values, remove duplicates, outlier detection, scaling, encoding).
- [ ] **EDA**: Automatically generated statistics, numerical/categorical analysis, correlation, distributions, relationship plots.
- [ ] **VIZ**: Interactive dashboard charts (Recharts/Plotly: bar, line, scatter, box plot, correlation matrix, donut).
- [ ] **FE**: Feature engineering suggestions (constant/correlated features removal, scaling, selection).
- [ ] **ML**: Machine learning module supporting Regression, Classification, Clustering, and Forecasting with model evaluation metrics.
- [ ] **XAI**: Explainable AI showing feature importances (e.g., age, income contribution percentages).
- [ ] **CHAT**: Gemini-powered AI chat assistant to ask questions and get insights using the dataset context.
- [ ] **INSIGHTS**: Automatically generated business recommendations and insights from data trends.
- [ ] **REPORT**: Downloadable PDF report generator covering dataset overview, EDA, visualizations, ML results, and AI recommendations.
- [ ] **NOTIFICATION**: System notifications for dataset uploads, analysis completion, model training, and report generation.
- [ ] **SEARCH**: Search projects, reports, datasets, and models.
- [ ] **PROFILE**: User profile management with project lists, reports, and chat history.

### Out of Scope

- [ ] Google OAuth — Deferred to Phase 5.
- [ ] Email Verification — Deferred to Phase 5.
- [ ] JSON, SQL Connection, Google Sheets import — Deferred to Phase 5.
- [ ] LSTM and Transformer-based Forecasting — Deferred to Phase 5.
- [ ] SHAP and LIME Explainability — Deferred to Phase 5.
- [ ] AutoML and MLOps Pipeline — Deferred to Phase 5.

## Context

Businesses, startups, and students often lack the coding expertise to analyze their data. InsightAI offers an end-to-end full-stack solution with a React/Next.js frontend, a FastAPI backend, MongoDB Atlas database, and the Gemini API for natural language analysis and report generation.

## Constraints

- **Database**: MongoDB Atlas.
- **Backend**: FastAPI with Python, REST APIs, JWT Auth.
- **Frontend**: Next.js, React, Tailwind CSS, TypeScript, Recharts, Plotly.
- **ML Engine**: Pandas, NumPy, Scikit-learn, XGBoost, Prophet.
- **AI Engine**: Gemini API.
- **Storage**: Local filesystem for development; Cloudinary/S3/GCS for production.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| FastAPI Backend | High performance, automatic Swagger/OpenAPI docs, Python ML ecosystem compatibility. | — Pending |
| MongoDB Database | Flexible, document-based schema suited for storing heterogeneous dataset metadata, model configurations, and chat histories. | — Pending |
| Next.js Frontend | Production-ready React framework with folder-based routing, static optimization, and standard styling with Tailwind. | — Pending |
| Gemini API | State-of-the-art LLM provider with large context window for ingesting structured dataset tables and generating business insights. | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-07-08 after initialization*
