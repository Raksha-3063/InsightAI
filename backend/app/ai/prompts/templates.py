import json
from typing import Dict, Any

COPILOT_SYSTEM_INSTRUCTION = (
    "You are Antigravity, the Enterprise AI Analytics Copilot for InsightAI. "
    "Your objective is to act as a world-class Business Intelligence and data science assistant. "
    "You help users understand their datasets, data quality anomalies, cleaning operations, statistical distributions, "
    "machine learning pipelines, feature importances, SHAP/LIME charts, time-series forecasting projections, and business risks.\n\n"
    "CRITICAL RULES:\n"
    "1. NEVER fabricate statistics, scores, or names. Only reference the exact computed metrics provided in the workspace context.\n"
    "2. Base your insights on mathematical truth. If the user asks a question not solvable with the context, state it clearly.\n"
    "3. Keep summaries concise, professional, and action-oriented."
)

def format_dataset_summary_prompt(context: Dict[str, Any]) -> str:
    return (
        f"Generate a professional dataset summary based on the following computed workspace context:\n\n"
        f"{json.dumps(context, indent=2)}\n\n"
        f"Please explain the columns catalog, row and column counts, missing values, duplicates, and general data quality. "
        f"Provide 3 actionable bullet-point observations."
    )

def format_model_comparison_prompt(context: Dict[str, Any]) -> str:
    return (
        f"Compare all trained machine learning pipelines using the following workspace context:\n\n"
        f"{json.dumps(context['machineLearningModels'], indent=2)}\n\n"
        f"Please detail which algorithm performs best, compare their validation metrics (e.g. Accuracy, F1-score, or R-squared), "
        f"and explain feature contribution trends based on feature importances."
    )

def format_forecast_explanation_prompt(context: Dict[str, Any]) -> str:
    return (
        f"Analyze the trained forecasting pipelines based on the following context:\n\n"
        f"{json.dumps(context['forecastingModels'], indent=2)}\n\n"
        f"Explain what the forecast results mean, details of the target variables, forecast horizon, "
        f"and evaluation metrics like MAPE/RMSE."
    )

def format_report_generation_prompt(context: Dict[str, Any]) -> str:
    return (
        f"Generate a comprehensive, publication-quality AI Executive Analytics Report for the following workspace context:\n\n"
        f"{json.dumps(context, indent=2)}\n\n"
        f"Construct a structured Markdown report containing these exact sections:\n"
        f"1. Executive Summary\n"
        f"2. Dataset Overview & Data Quality (citing rows, cols, health score)\n"
        f"3. Cleaning Operations Audit\n"
        f"4. Machine Learning Models Performance & SHAP Interpretability\n"
        f"5. Time Series Forecast Trends\n"
        f"6. Business Recommendations & Suggested Next Steps\n\n"
        f"Make sure to reference exact numerical coefficients and values from the context."
    )

def format_recommendations_prompt(context: Dict[str, Any]) -> str:
    return (
        f"Generate optimization recommendations for the data science workflow using the following context:\n\n"
        f"{json.dumps(context, indent=2)}\n\n"
        f"Recommend: best model choices, feature engineering opportunities (log-scaling, date extraction), "
        f"multicollinearity removals, and outlier handling. Cite evidence coefficients from the context."
    )

def format_general_chat_prompt(message: str, context: Dict[str, Any]) -> str:
    return (
        f"User Question: \"{message}\"\n\n"
        f"Workspace Context:\n"
        f"{json.dumps(context, indent=2)}\n\n"
        f"Answer the user's question accurately using the provided workspace context details. "
        f"Cite computed metrics where applicable. If the context does not contain the answer, answer honestly using standard data science best practices."
    )
