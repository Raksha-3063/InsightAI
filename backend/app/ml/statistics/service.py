import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List

def clean_float(val: Any) -> Any:
    """
    Ensure float values are JSON serializable (converts NaN, inf, -inf to None).
    """
    if pd.isna(val) or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
        return None
    return float(val)

def calculate_numerical_statistics(df: pd.DataFrame, num_cols: List[str]) -> Dict[str, Any]:
    """
    Calculate descriptive statistics for numerical columns in a DataFrame.
    """
    stats = {}
    for col in num_cols:
        if col not in df.columns:
            continue
            
        series = df[col].dropna()
        if series.empty:
            stats[col] = {
                "mean": None, "median": None, "mode": None,
                "variance": None, "std": None, "min": None, "max": None,
                "range": None, "q25": None, "q50": None, "q75": None,
                "skewness": None, "kurtosis": None
            }
            continue

        mode_series = series.mode()
        mode_val = clean_float(mode_series[0]) if not mode_series.empty else None

        stats[col] = {
            "mean": clean_float(series.mean()),
            "median": clean_float(series.median()),
            "mode": mode_val,
            "variance": clean_float(series.var()),
            "std": clean_float(series.std()),
            "min": clean_float(series.min()),
            "max": clean_float(series.max()),
            "range": clean_float(series.max() - series.min()),
            "q25": clean_float(series.quantile(0.25)),
            "q50": clean_float(series.quantile(0.50)),
            "q75": clean_float(series.quantile(0.75)),
            "skewness": clean_float(series.skew()),
            "kurtosis": clean_float(series.kurt())
        }
    return stats

def calculate_categorical_statistics(df: pd.DataFrame, cat_cols: List[str]) -> Dict[str, Any]:
    """
    Calculate frequencies and descriptive parameters for categorical columns.
    """
    stats = {}
    rows = len(df)
    for col in cat_cols:
        if col not in df.columns:
            continue
            
        series = df[col].dropna()
        unique_vals = series.unique()
        cardinality = len(unique_vals)
        cardinality_ratio = float(cardinality / rows) if rows > 0 else 0.0
        
        # Calculate class frequencies
        value_counts = series.value_counts()
        frequencies = {str(k): int(v) for k, v in value_counts.items()}
        
        top_cat = str(value_counts.idxmax()) if not value_counts.empty else None
        top_cat_count = int(value_counts.max()) if not value_counts.empty else 0

        stats[col] = {
            "uniqueValues": cardinality,
            "cardinalityRatio": clean_float(cardinality_ratio),
            "frequencies": frequencies,
            "topCategory": top_cat,
            "topCategoryCount": top_cat_count
        }
    return stats

def calculate_correlations(df: pd.DataFrame, num_cols: List[str]) -> Dict[str, Any]:
    """
    Calculate Pearson and Spearman correlation matrices across numerical columns.
    """
    if len(num_cols) < 2:
        return {
            "columns": num_cols,
            "pearson": [],
            "spearman": []
        }
        
    df_num = df[num_cols].dropna()
    if df_num.empty or len(df_num) < 2:
        return {
            "columns": num_cols,
            "pearson": [],
            "spearman": []
        }

    # Pearson correlation matrix
    pearson_df = df_num.corr(method="pearson")
    pearson_matrix = []
    for i, col1 in enumerate(num_cols):
        row = []
        for j, col2 in enumerate(num_cols):
            val = pearson_df.loc[col1, col2] if col1 in pearson_df.index and col2 in pearson_df.columns else None
            row.append(clean_float(val))
        pearson_matrix.append(row)

    # Spearman correlation matrix
    spearman_df = df_num.corr(method="spearman")
    spearman_matrix = []
    for i, col1 in enumerate(num_cols):
        row = []
        for j, col2 in enumerate(num_cols):
            val = spearman_df.loc[col1, col2] if col1 in spearman_df.index and col2 in spearman_df.columns else None
            row.append(clean_float(val))
        spearman_matrix.append(row)

    return {
        "columns": num_cols,
        "pearson": pearson_matrix,
        "spearman": spearman_matrix
    }
