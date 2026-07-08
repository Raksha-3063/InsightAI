# Roadmap: InsightAI

## Overview

InsightAI is built phase-by-phase using a Vertical MVP approach. Each phase delivers a complete end-to-end slice of functionality, taking the user from basic dataset ingestion up to advanced AI-powered chat and report generation.

## Phases

- [ ] **Phase 1: Foundation & Dataset Ingestion** - JWT authentication, MongoDB schema, project separation, and CSV/Excel file uploads.
- [ ] **Phase 2: Data Cleaning & Exploratory Data Analysis (EDA)** - Automated cleaning operations, statistical profiles, and interactive chart visualizations.
- [ ] **Phase 3: Machine Learning Engine & Forecasting** - Core Regression, Classification, Clustering, and time-series forecasting.
- [ ] **Phase 4: AI Chat, Explainable AI & Report Generation** - Gemini API chat assistant, explainable AI model summaries, and PDF report downloads.

## Phase Details

### Phase 1: Foundation & Dataset Ingestion

**Goal**: Basic user setup, project isolation, and dataset uploads with metadata generation.
**Mode**: mvp
**Depends on**: Nothing (first phase)
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04, PROJ-01, PROJ-02, PROJ-03, DATA-01, DATA-02, DATA-03, DATA-04
**Success Criteria** (what must be TRUE):

  1. User can register, login, and persist their session.
  2. User can create new projects and isolate their workspace.
  3. User can upload CSV or Excel files, which parse successfully and store rows, columns, and missing-value summaries in MongoDB.

**Plans**: 3 plans

Plans:
**Wave 1**

- [ ] 01-01: Backend API Setup (FastAPI structure, MongoDB integration, Auth, JWT)

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 01-02: Project and Dataset Upload APIs (Upload, file verification, local storage, metadata parser)

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 01-03: Frontend Dashboard UI (Auth views, project management list, file uploader component, dataset summary display)

### Phase 2: Data Cleaning & Exploratory Data Analysis (EDA)

**Goal**: Automated data cleaning actions and statistical profile visualizations.
**Mode**: mvp
**Depends on**: Phase 1
**Requirements**: CLNT-01, CLNT-02, CLNT-03, CLNT-04, CLNT-05, CLNT-06, EDAA-01, EDAA-02, EDAA-03, EDAA-04, VIZZ-01, VIZZ-02
**Success Criteria** (what must be TRUE):

  1. User can trigger cleaning steps (Mean/Median imputation, dropping rows, scaling, encoding) and see the updated schema.
  2. Numerical summaries (mean, variance, skewness) and categorical distributions generate automatically.
  3. UI renders interactive charts (Histograms, Scatter, Line, Heatmap, Box plots) based on dataset columns.

**Plans**: 3 plans

Plans:

- [ ] 02-01: Data Cleaning Module & APIs (Pandas-based missing value handling, duplicate removal, outlier detection, scaling, encoding)
- [ ] 02-02: Automated EDA & Correlation APIs (Numerical summaries, categorical distribution, correlation matrix calculation)
- [ ] 02-03: Interactive Chart Visualizations & Dashboard UI (Interactive charts using Recharts/Plotly, dataset health card, cleaning UI panel)

### Phase 3: Machine Learning Engine & Forecasting

**Goal**: Core Regression, Classification, Clustering, and time-series forecasting.
**Mode**: mvp
**Depends on**: Phase 2
**Requirements**: FEEN-01, FEEN-02, MACH-01, MACH-02, MACH-03, MACH-04, MACH-05
**Success Criteria** (what must be TRUE):

  1. User can train Regression and Classification models and view metrics (R², Accuracy, Confusion Matrix).
  2. User can perform clustering (K-Means/DBSCAN) and view cluster scatter plots and summaries.
  3. User can run time-series forecasting (ARIMA/Prophet) and view future trends with confidence intervals.

**Plans**: 4 plans

Plans:

- [ ] 03-01: ML Engine: Regression & Classification (Model training, evaluation metrics, feature importances, local model path storage)
- [ ] 03-02: ML Engine: Clustering (K-Means/DBSCAN, summaries, Silhouette Score)
- [ ] 03-03: Forecasting Module (Prophet and ARIMA integration for date-indexed columns, confidence bounds)
- [ ] 03-04: Model Dashboards & Visualizations UI (Select models, train models, show evaluation stats, residual/ROC/confusion matrix charts)

### Phase 4: AI Chat, Explainable AI & Report Generation

**Goal**: Gemini API chat assistant, explainable AI model summaries, and PDF report downloads.
**Mode**: mvp
**Depends on**: Phase 3
**Requirements**: EXAI-01, EXAI-02, CHAT-01, CHAT-02, REPT-01, REPT-02, NTFY-01
**Success Criteria** (what must be TRUE):

  1. User can ask natural language questions in a chat interface and receive answers grounded in their dataset context.
  2. Model-independent feature importances and contributions are explained in plain text.
  3. User can download a professional PDF report summarizing EDA, ML results, and AI recommendations.

**Plans**: 3 plans

Plans:

- [ ] 04-01: Gemini API Chat Assistant & Insights (Dataset metadata/summary injection, prompt structuring, explainable AI explanations)
- [ ] 04-02: PDF Report Generator (ReportLab or similar to compile EDA summaries, ML metrics, and AI recommendations into PDF)
- [ ] 04-03: AI Chat Interface, PDF Download & Notifications (Chat UI components, download action, and in-app success notifications)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Dataset Ingestion | 0/3 | Not started | - |
| 2. Data Cleaning & EDA | 0/3 | Not started | - |
| 3. ML Engine & Forecasting | 0/4 | Not started | - |
| 4. AI Chat, XAI & Reports | 0/3 | Not started | - |
