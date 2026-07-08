# Requirements: InsightAI

**Defined:** 2026-07-08
**Core Value:** Eliminate the need for manual Jupyter notebook creation by providing a professional, automated analytics dashboard, predictive models, AI-generated reports, and an intelligent chatbot for uploaded data.

## v1 Requirements

Requirements for the initial release of InsightAI. Each maps to roadmap phases.

### Authentication & Profiles

- [x] **AUTH-01**: User can register an account with name, email, and password.
- [x] **AUTH-02**: User can log in and receive a secure JWT token.
- [x] **AUTH-03**: User session persists across refreshes using localStorage/secure cookies.
- [x] **AUTH-04**: User can view and update their profile.

### Project Management

- [x] **PROJ-01**: User can create a new project with a name and description.
- [x] **PROJ-02**: User can view a dashboard listing all their projects.
- [x] **PROJ-03**: User can view project-specific metrics, recent uploads, models, and reports.

### Dataset Ingestion & Storage

- [x] **DATA-01**: User can upload datasets in CSV and Excel (.xlsx) formats.
- [x] **DATA-02**: System validates the uploaded file (size, format, headers) and reads structure.
- [x] **DATA-03**: System stores dataset metadata (rows, columns, missing values, duplicate count, column types) in MongoDB.
- [x] **DATA-04**: Original files are saved to local filesystem storage (development setup).

### Data Cleaning Module

- [ ] **CLNT-01**: System automatically detects duplicates, missing values, incorrect data types, and outliers.
- [ ] **CLNT-02**: User can clean missing values by replacing them (Mean, Median, Mode) or dropping rows/columns.
- [ ] **CLNT-03**: User can remove duplicate rows.
- [ ] **CLNT-04**: User can detect/handle outliers using IQR or Z-score methods.
- [ ] **CLNT-05**: User can scale features (Standardization, Normalization).
- [ ] **CLNT-06**: User can encode categorical features (One-Hot Encoding, Label Encoding, Ordinal Encoding).

### Exploratory Data Analysis (EDA)

- [ ] **EDAA-01**: System generates statistical summaries for numerical columns (mean, median, variance, skewness, kurtosis, etc.).
- [ ] **EDAA-02**: System generates frequency distributions and unique counts for categorical columns.
- [ ] **EDAA-03**: System computes Pearson correlation matrix across numerical columns.
- [ ] **EDAA-04**: System extracts weekly, monthly, and daily trends if a date/time column is present.

### Visualizations & Dashboard

- [ ] **VIZZ-01**: Dashboard displays key KPI cards (Total Rows, Columns, Missing Values, Dataset Health score).
- [ ] **VIZZ-02**: System renders interactive charts: Histogram, Pie/Donut Chart, Bar Chart, Line Chart, Scatter Plot, Heatmap, Box Plot, and Correlation Matrix.

### Feature Engineering

- [ ] **FEEN-01**: System suggests removing constant features (variance ~ 0) or highly correlated features (> 0.9).
- [ ] **FEEN-02**: System calculates simple statistical feature importance metrics.

### Machine Learning Engine

- [ ] **MACH-01**: User can run Regression (Linear, Ridge, Lasso, Decision Tree, Random Forest, XGBoost) and see metrics (MAE, MSE, RMSE, R²).
- [ ] **MACH-02**: User can run Classification (Logistic Regression, Decision Tree, Random Forest, Naive Bayes, SVM, XGBoost) and see metrics (Accuracy, Precision, Recall, F1, ROC Curve, Confusion Matrix).
- [ ] **MACH-03**: User can run Clustering (K-Means, DBSCAN, Hierarchical) and see Silhouette Score and cluster summaries.
- [ ] **MACH-04**: User can run Forecasting (ARIMA, Prophet) and view trends, forecasts, and confidence intervals.
- [ ] **MACH-05**: System renders ML-specific plots (Actual vs Predicted, Residual plot, ROC Curve, Confusion Matrix heatmap, Cluster scatter plot).

### Explainable AI & Insights

- [ ] **EXAI-01**: System extracts and visualizes feature importance percentages for trained models.
- [ ] **EXAI-02**: System generates natural language explanations of what features contributed most to the model.

### AI Chat Assistant

- [ ] **CHAT-01**: User can ask questions about the dataset in a chat interface.
- [ ] **CHAT-02**: System compiles dataset context (summary statistics, sample data) and passes it to the Gemini API to return grounded, data-backed answers.

### AI Business Insights & Reports

- [ ] **REPT-01**: System automatically generates business insights (e.g. sales trends, anomalies) using Gemini based on dataset characteristics.
- [ ] **REPT-02**: User can generate and download a professional PDF report containing the Executive Summary, EDA results, ML evaluations, and AI recommendations.

### Notifications

- [ ] **NTFY-01**: In-app notifications inform the user when upload, cleaning, model training, or report generation is completed.

---

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Enterprise Features

- **AUTH-05**: Google OAuth and Email verification on signup.
- **DATA-05**: Connect directly to SQL databases or Google Sheets.
- **REPT-03**: Scheduled reports sent automatically to email.
- **COLL-01**: Shared workspaces and team collaboration.

### Advanced ML/AI

- **MACH-06**: Deep learning forecasting using LSTM or Transformer-based models.
- **EXAI-03**: Integrate formal SHAP and LIME libraries for local and global model explainability.
- **CHAT-03**: RAG (Retrieval-Augmented Generation) on multi-document uploads using vector databases.
- **AUTO-01**: AutoML engine to automatically find the best algorithm and hyperparameters.

---

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Multi-file joins | Processing multiple uploaded files simultaneously is deferred due to schema mapping complexity. |
| Production cloud deployment | Development environment uses local storage and local MongoDB; cloud storage (S3/GCS) and production Vercel/Railway deployments are deferred. |
| Custom model code upload | Users select from pre-packaged ML algorithms; uploading arbitrary Scikit-learn/TensorFlow scripts is out of scope. |

---

## Traceability

Which roadmap phases cover which requirements.

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01     | Phase 1 | Complete |
| AUTH-02     | Phase 1 | Complete |
| AUTH-03     | Phase 1 | Complete |
| AUTH-04     | Phase 1 | Complete |
| PROJ-01     | Phase 1 | Complete |
| PROJ-02     | Phase 1 | Complete |
| PROJ-03     | Phase 1 | Complete |
| DATA-01     | Phase 1 | Complete |
| DATA-02     | Phase 1 | Complete |
| DATA-03     | Phase 1 | Complete |
| DATA-04     | Phase 1 | Complete |
| CLNT-01     | Phase 2 | Pending |
| CLNT-02     | Phase 2 | Pending |
| CLNT-03     | Phase 2 | Pending |
| CLNT-04     | Phase 2 | Pending |
| CLNT-05     | Phase 2 | Pending |
| CLNT-06     | Phase 2 | Pending |
| EDAA-01     | Phase 2 | Pending |
| EDAA-02     | Phase 2 | Pending |
| EDAA-03     | Phase 2 | Pending |
| EDAA-04     | Phase 2 | Pending |
| VIZZ-01     | Phase 2 | Pending |
| VIZZ-02     | Phase 2 | Pending |
| FEEN-01     | Phase 3 | Pending |
| FEEN-02     | Phase 3 | Pending |
| MACH-01     | Phase 3 | Pending |
| MACH-02     | Phase 3 | Pending |
| MACH-03     | Phase 3 | Pending |
| MACH-04     | Phase 3 | Pending |
| MACH-05     | Phase 3 | Pending |
| EXAI-01     | Phase 4 | Pending |
| EXAI-02     | Phase 4 | Pending |
| CHAT-01     | Phase 4 | Pending |
| CHAT-02     | Phase 4 | Pending |
| REPT-01     | Phase 4 | Pending |
| REPT-02     | Phase 4 | Pending |
| NTFY-01     | Phase 4 | Pending |

**Coverage:**

- v1 requirements: 37 total
- Mapped to phases: 37
- Unmapped: 0 ✓

---
*Requirements defined: 2026-07-08*
*Last updated: 2026-07-08 after initial definition*
