import math
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from app.ml.statistics.service import clean_float

def generate_histogram_data(df: pd.DataFrame, col: str, bins_count: int = 10) -> List[Dict[str, Any]]:
    """
    Generate bin boundaries and frequency counts for a numerical column.
    """
    series = df[col].dropna()
    if series.empty:
        return []
        
    counts, edges = np.histogram(series, bins=bins_count)
    data = []
    for i in range(len(counts)):
        label = f"{clean_float(edges[i]):.2f} - {clean_float(edges[i+1]):.2f}"
        data.append({
            "binName": label,
            "count": int(counts[i]),
            "min": clean_float(edges[i]),
            "max": clean_float(edges[i+1])
        })
    return data

def generate_box_plot_data(df: pd.DataFrame, col: str) -> Dict[str, Any]:
    """
    Calculate statistics required for a box and whisker plot: Min, Q1, Median, Q3, Max, and Outliers.
    """
    series = df[col].dropna()
    if series.empty:
        return {
            "min": None, "q1": None, "median": None, "q3": None, "max": None, "outliers": []
        }
        
    q1 = series.quantile(0.25)
    median = series.median()
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    
    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr
    
    # Non-outlier min and max
    non_outliers = series[(series >= lower_fence) & (series <= upper_fence)]
    min_val = non_outliers.min() if not non_outliers.empty else series.min()
    max_val = non_outliers.max() if not non_outliers.empty else series.max()
    
    # Outliers list (limit to 100 points for performance)
    outliers = series[(series < lower_fence) | (series > upper_fence)]
    if len(outliers) > 100:
        outliers = outliers.sample(n=100, random_state=42)
        
    return {
        "min": clean_float(min_val),
        "q1": clean_float(q1),
        "median": clean_float(median),
        "q3": clean_float(q3),
        "max": clean_float(max_val),
        "outliers": [clean_float(v) for v in outliers]
    }

def generate_scatter_data(df: pd.DataFrame, col_x: str, col_y: str, max_points: int = 500) -> List[Dict[str, Any]]:
    """
    Generate downsampled scatter coordinates for two numerical columns.
    """
    sub_df = df[[col_x, col_y]].dropna()
    if len(sub_df) > max_points:
        sub_df = sub_df.sample(n=max_points, random_state=42)
        
    return [
        {"x": clean_float(row[col_x]), "y": clean_float(row[col_y])}
        for _, row in sub_df.iterrows()
    ]

def generate_pie_chart_data(df: pd.DataFrame, col: str, max_slices: int = 5) -> List[Dict[str, Any]]:
    """
    Generate category slices and percentages, grouping lesser categories into 'Other'.
    """
    series = df[col].dropna()
    if series.empty:
        return []
        
    counts = series.value_counts()
    total = int(counts.sum())
    
    slices = []
    other_count = 0
    
    for i, (cat, count) in enumerate(counts.items()):
        if i < max_slices:
            slices.append({
                "name": str(cat),
                "value": int(count),
                "percentage": clean_float((count / total) * 100)
            })
        else:
            other_count += count
            
    if other_count > 0:
        slices.append({
            "name": "Other",
            "value": int(other_count),
            "percentage": clean_float((other_count / total) * 100)
        })
        
    return slices

def generate_bar_chart_data(df: pd.DataFrame, col: str, max_bars: int = 10) -> List[Dict[str, Any]]:
    """
    Generate frequencies for a categorical column, limiting to the top categories.
    """
    series = df[col].dropna()
    if series.empty:
        return []
        
    counts = series.value_counts().head(max_bars)
    return [
        {"category": str(k), "count": int(v)}
        for k, v in counts.items()
    ]

def generate_line_chart_data(df: pd.DataFrame, date_col: str, num_col: str, max_points: int = 100) -> List[Dict[str, Any]]:
    """
    Generate date-based values, grouping/sorting by date.
    """
    sub_df = df[[date_col, num_col]].dropna()
    if sub_df.empty:
        return []
        
    # Group by date column (convert to string date format)
    # If date_col is not yet datetime, parse it
    if not pd.api.types.is_datetime64_any_dtype(sub_df[date_col].dtype):
        try:
            sub_df[date_col] = pd.to_datetime(sub_df[date_col])
        except Exception:
            return []
            
    # Sort and aggregate by date (take mean)
    sub_df["date_str"] = sub_df[date_col].dt.strftime("%Y-%m-%d")
    grouped = sub_df.groupby("date_str")[num_col].mean().reset_index()
    grouped = grouped.sort_values("date_str")
    
    # Downsample if needed by skipping rows
    if len(grouped) > max_points:
        step = int(len(grouped) / max_points)
        grouped = grouped.iloc[::step]
        
    return [
        {"date": str(row["date_str"]), "value": clean_float(row[num_col])}
        for _, row in grouped.iterrows()
    ]
