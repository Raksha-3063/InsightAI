import pandas as pd
import numpy as np
from typing import Dict, Any, List
from app.ml.statistics.service import clean_float

def calculate_dataset_health(df: pd.DataFrame, profiling_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate a health score (0-100), identify strengths, warnings, and cleaning recommendations.
    """
    rows = profiling_data["rows"]
    cols = profiling_data["columns"]
    total_cells = rows * cols
    
    if total_cells == 0:
        return {
            "score": 0,
            "strengths": [],
            "warnings": ["Dataset is empty."],
            "recommendations": ["Upload a valid CSV/Excel file."]
        }
        
    score = 100
    strengths = []
    warnings = []
    recommendations = []
    
    # 1. Missing Values check
    total_missing = profiling_data["missingValues"]
    missing_ratio = total_missing / total_cells
    missing_percentage = missing_ratio * 100
    
    if total_missing == 0:
        strengths.append("No missing values detected.")
    else:
        # Deduct up to 30 points
        deduction = min(30, int(missing_ratio * 100))
        score -= deduction
        warnings.append(f"Missing values occupy {missing_percentage:.1f}% of total cells.")
        recommendations.append("Apply Imputation (Mean, Median, or Mode) to clean missing values.")

    # 2. Duplicate Rows check
    total_duplicates = profiling_data["duplicateRows"]
    duplicate_ratio = total_duplicates / rows if rows > 0 else 0.0
    duplicate_percentage = duplicate_ratio * 100
    
    if total_duplicates == 0:
        strengths.append("No duplicate rows found.")
    else:
        # Deduct up to 15 points
        deduction = min(15, int(duplicate_ratio * 100))
        score -= deduction
        warnings.append(f"Duplicate rows account for {duplicate_percentage:.1f}% of the dataset.")
        recommendations.append("Remove duplicate rows using the duplicate removal action.")

    # 3. Outlier check (Numerical columns)
    num_cols = profiling_data["numericalColumns"]
    total_outliers = 0
    total_num_cells = 0
    
    for col in num_cols:
        if col not in df.columns:
            continue
        series = df[col].dropna()
        if series.empty:
            continue
            
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        
        outliers_count = len(series[(series < lower_fence) | (series > upper_fence)])
        total_outliers += outliers_count
        total_num_cells += len(series)

    if total_num_cells > 0:
        outlier_ratio = total_outliers / total_num_cells
        outlier_percentage = outlier_ratio * 100
        if outlier_percentage > 5:
            # Deduct up to 10 points
            deduction = min(10, int((outlier_percentage - 5) * 0.5))
            score -= deduction
            warnings.append(f"Significant outliers detected in numerical columns ({outlier_percentage:.1f}% of values).")
            recommendations.append("Handle outliers using IQR/Z-score clipping or dropping.")
        elif outlier_percentage == 0:
            strengths.append("Numerical data is free of extreme outliers.")
            
    # 4. Data Cardinality / Type Consistency
    text_cols = profiling_data["textColumns"]
    if len(text_cols) > 0:
        warnings.append(f"High-cardinality text columns detected: {', '.join(text_cols[:3])}.")
        recommendations.append("Consider dropping ID or unique text columns to improve model performance.")
        
    # 5. Row-to-Column Ratio
    if cols > 0:
        ratio = rows / cols
        if ratio < 10:
            score -= 10
            warnings.append("Low row-to-column ratio (fewer than 10 rows per column). Highly vulnerable to overfitting.")
            recommendations.append("Collect more data rows or drop non-essential features/columns.")
        elif ratio > 100:
            strengths.append("High row-to-column ratio, providing strong support for statistical models.")

    # Bound health score to 0 - 100
    score = max(0, min(100, score))
    
    return {
        "score": score,
        "strengths": strengths,
        "warnings": warnings,
        "recommendations": recommendations
    }

def generate_dataset_insights(df: pd.DataFrame, profiling_data: Dict[str, Any], stats_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate deterministic insights (most skewed feature, highly correlated columns, prediction target recommendation).
    """
    insights = []
    
    # 1. High correlation insight
    num_cols = profiling_data["numericalColumns"]
    if len(num_cols) >= 2:
        df_num = df[num_cols].dropna()
        if not df_num.empty and len(df_num) >= 2:
            corr_df = df_num.corr(method="pearson").abs()
            high_corrs = []
            
            for i in range(len(num_cols)):
                for j in range(i + 1, len(num_cols)):
                    col1 = num_cols[i]
                    col2 = num_cols[j]
                    val = corr_df.loc[col1, col2] if col1 in corr_df.index and col2 in corr_df.columns else 0.0
                    if val > 0.85:
                        high_corrs.append((col1, col2, val))
                        
            if high_corrs:
                pairs_str = ", ".join([f"({c1} & {c2}: {v:.2f})" for c1, c2, v in high_corrs[:3]])
                insights.append({
                    "title": "Multicollinearity Danger",
                    "description": f"Highly correlated feature pairs detected: {pairs_str}.",
                    "type": "warning",
                    "action": "Consider removing one of the features to reduce model redundancy."
                })

    # 2. Extreme Skewness
    highest_skew = 0.0
    skewed_col = None
    for col in num_cols:
        col_stats = stats_data.get(col, {})
        skew = col_stats.get("skewness")
        if skew is not None and abs(skew) > highest_skew:
            highest_skew = abs(skew)
            skewed_col = col
            
    if skewed_col and highest_skew > 2.0:
        insights.append({
            "title": "Highly Skewed Features",
            "description": f"Feature '{skewed_col}' exhibits extreme skewness ({highest_skew:.2f}).",
            "type": "info",
            "action": "Consider applying Standard/MinMax scaling or log transformation to normalize its distribution."
        })

    # 3. Target suggestion insight
    target = profiling_data["targetSuggestion"]
    if target:
        target_type = profiling_data["columnTypes"].get(target, "unknown")
        task_type = "Classification" if target_type in ["categorical", "boolean"] else "Regression"
        insights.append({
            "title": "Target Column Suggestion",
            "description": f"Recommended target: '{target}' (classified as {target_type} data).",
            "type": "success",
            "action": f"Train a {task_type} model to predict values in this column during ML phases."
        })

    # 4. Constant columns
    constant_cols = []
    for col in df.columns:
        non_null_series = df[col].dropna()
        if len(non_null_series.unique()) == 1:
            constant_cols.append(str(col))
            
    if constant_cols:
        insights.append({
            "title": "Zero Variance Columns",
            "description": f"Columns with constant values: {', '.join(constant_cols)}.",
            "type": "warning",
            "action": "Remove constant columns as they provide no predictive information."
        })

    return insights
