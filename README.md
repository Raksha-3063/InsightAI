# 🚀 InsightAI

> **An Enterprise AI-Powered Business Intelligence Platform for Automated Data Analytics, Machine Learning, Explainable AI, Forecasting, and AI-Assisted Business Insights.**

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=for-the-badge&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-15-black?style=for-the-badge&logo=next.js)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?style=for-the-badge&logo=mongodb)
![TypeScript](https://img.shields.io/badge/TypeScript-blue?style=for-the-badge&logo=typescript)
![Docker](https://img.shields.io/badge/Docker-blue?style=for-the-badge&logo=docker)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

---

# 📌 Overview

InsightAI is an enterprise-grade AI analytics platform that transforms raw datasets into meaningful business insights using Machine Learning, Explainable AI, Forecasting, and Generative AI.

Instead of manually performing data preprocessing, visualization, model training, and reporting, InsightAI automates the complete analytics workflow through an intuitive web interface.

---

# ✨ Features

## 📂 Dataset Management

- Upload CSV & Excel datasets
- Multiple projects support
- Secure authentication (JWT)
- MongoDB-based storage
- Dataset versioning

---

## 📊 Automated Data Profiling

- Dataset summary
- Missing value analysis
- Duplicate detection
- Data type identification
- Statistical summaries
- Correlation analysis
- Dataset Health Score
- Automatic insights generation

---

## 🧹 Data Cleaning

- Missing value imputation
- Outlier detection
- Feature scaling
- Feature encoding
- Cleaning history
- Undo operations

---

## 📈 Interactive Visualizations

- Histograms
- Scatter plots
- Correlation heatmaps
- Box plots
- Line charts
- Pie charts
- Distribution analysis

---

## 🤖 Machine Learning

Supports:

- Linear Regression
- Logistic Regression
- Random Forest
- Decision Tree
- XGBoost
- K-Means Clustering

Automatically provides:

- Model comparison
- Evaluation metrics
- Feature importance
- Model persistence
- Batch prediction

---

## 📉 Time Series Forecasting

- Prophet
- ARIMA
- Automatic time-series detection
- Forecast visualization
- Confidence intervals

---

## 🔍 Explainable AI (XAI)

- SHAP explanations
- LIME explanations
- Feature importance
- Business recommendations
- Model interpretation

---

## 🧠 AI Copilot

Powered by Google's Gemini API.

Capabilities include:

- Dataset summarization
- Business insights
- Model explanation
- Forecast interpretation
- AI-generated recommendations
- Executive report generation

---

## 📄 Reporting

Generate reports in:

- Markdown
- HTML
- PDF

Reports include:

- Executive Summary
- Data Overview
- ML Results
- Forecasts
- Explainability
- AI Recommendations

---

## 🔐 Authentication

- JWT Authentication
- User Registration
- Login
- Protected APIs
- Role-based architecture

---

## ⚙️ Production Features

- Docker support
- Celery background jobs
- Redis task queue
- MLflow experiment tracking
- Prometheus monitoring
- GitHub Actions CI/CD

---

# 🏗️ System Architecture

```text
                User
                  │
                  ▼
         Next.js Frontend
                  │
         REST API (FastAPI)
                  │
    ┌─────────────┼──────────────┐
    │             │              │
 MongoDB       ML Engine     AI Copilot
    │             │              │
    │       Forecasting      Gemini API
    │             │
    └────── Explainable AI ─────┘
                  │
           Report Generation
```

---

# 🛠️ Tech Stack

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- Axios

### Backend

- FastAPI
- Python
- JWT Authentication
- Pydantic

### Database

- MongoDB Atlas

### Machine Learning

- Pandas
- NumPy
- Scikit-Learn
- XGBoost
- SHAP
- LIME
- Prophet
- StatsModels

### AI

- Google Gemini API

### DevOps

- Docker
- Redis
- Celery
- GitHub Actions
- MLflow
- Prometheus

---

# 📂 Project Structure

```
InsightAI/

├── backend/
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│
├── docs/
├── docker/
├── README.md
```

---

# 🚀 Getting Started

## Clone Repository

```bash
git clone https://github.com/Raksha-3063/InsightAI.git
```

```bash
cd InsightAI
```

---

## Backend

```bash
cd backend

pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# 📷 Screenshots

> Add screenshots here after deployment.

- Dashboard
- Dataset Upload
- Data Profiling
- Visualizations
- Machine Learning
- Forecasting
- Explainable AI
- AI Copilot

---

# 🎯 Future Enhancements

- LLM-powered SQL generation
- AutoML pipeline
- Multi-user collaboration
- Real-time dashboards
- Cloud deployment
- Role-based permissions
- Data lineage tracking

---

# 👩‍💻 Author

**Raksha C C**

- 💼 Aspiring AI/ML Engineer
- 🎓 Computer Science Engineering
- 🌱 Passionate about Artificial Intelligence, Data Science, and Full Stack Development

---

# ⭐ Support

If you found this project helpful, please consider giving it a ⭐ on GitHub!
