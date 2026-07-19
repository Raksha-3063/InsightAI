# User Guide: InsightAI

InsightAI helps business teams, analysts, and developers build predictive models, forecast trends, and ask questions of their data without writing code.

---

## 1. Project Ingestion & Profiling

1. Register or Log in to your InsightAI workspace.
2. Click **Create Project** to initialize a new dataset workspace.
3. Drag and drop your dataset file (CSV, Excel).
4. As soon as upload completes, InsightAI will show:
   * **Data Quality Score**: Number of missing values, anomalies, duplicate records.
   * **Visual Outliers**: Outliers identified in numeric fields.
   * **Correlation Matrices**: Heatmaps representing feature relationships.
   * **Clean Pipeline**: Apply quick operations (fill nulls, convert datatypes, normalize).

---

## 2. Machine Learning Engine

1. Navigate to the **Model Workspace** tab.
2. Choose your **Target Variable** (e.g. `Price`, `ChurnStatus`).
3. Select features to train with, choose an algorithm (Linear Regression, Random Forest, XGBoost), and click **Train**.
4. Once training finishes:
   * Explore performance metrics (R-squared, Accuracy, F1 score).
   * Review charts comparing predicted vs. actual coordinates.
   * Perform manual or file-based batch predictions.

---

## 3. Forecasting & Explainability

1. For time-series datasets, navigate to the **Forecasting** panel.
2. Set date column, target column, and click **Forecast** to project future metrics.
3. Click the **Explainability** tab to inspect SHAP global impact metrics and LIME feature contributions for single instances.

---

## 4. AI Analytics Copilot

1. Toggle the **AI Copilot** side panel.
2. Ask natural language questions like *"which feature has the highest correlation with price?"* or *"why did model accuracy drop?"*.
3. Click **Generate Executive Report** to render a PDF/HTML report summarising data quality, correlation insights, ML performance, and business suggestions.
