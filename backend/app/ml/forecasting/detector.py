import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

def detect_time_series(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Automatically analyze a dataframe to see if it is suitable for time series forecasting.
    """
    report = {
        "isFeasible": False,
        "datetimeColumn": None,
        "frequency": None,
        "missingTimestampsCount": 0,
        "targetCandidates": [],
        "warnings": [],
        "suggestedTarget": None
    }
    
    if len(df) < 10:
        report["warnings"].append("Dataset has too few rows (< 10) to perform time series forecasting.")
        return report

    # 1. Identify potential Datetime columns
    datetime_col = None
    
    # Check already inferred datetime columns
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            datetime_col = col
            break
            
    # Fallback: try parsing columns that look like dates or are of string type
    if not datetime_col:
        for col in df.columns:
            if df[col].dtype == 'object' or isinstance(df[col].iloc[0], str):
                # Try parsing a sample of 20 elements
                sample = df[col].dropna().head(20)
                if len(sample) > 5:
                    try:
                        parsed = pd.to_datetime(sample, errors='coerce')
                        # If more than 80% parsed successfully
                        if parsed.notna().sum() / len(sample) > 0.8:
                            datetime_col = col
                            break
                    except Exception:
                        pass
                        
    if not datetime_col:
        report["warnings"].append("No datetime column was identified in the dataset.")
        return report
        
    report["datetimeColumn"] = datetime_col
    
    # Try to parse the entire column
    try:
        dates = pd.to_datetime(df[datetime_col], errors='coerce')
        # If there are NaN values in parsed dates, warn and drop them for analysis
        if dates.isna().sum() > 0:
            report["warnings"].append(f"Datetime column '{datetime_col}' has missing values.")
            valid_indices = dates.notna()
            dates = dates[valid_indices]
            temp_df = df[valid_indices].copy()
        else:
            temp_df = df.copy()
            
        # Sort values chronologically
        sort_order = dates.argsort()
        dates = dates.iloc[sort_order].reset_index(drop=True)
        temp_df = temp_df.iloc[sort_order].reset_index(drop=True)
        
    except Exception as e:
        report["warnings"].append(f"Failed to parse datetime column '{datetime_col}': {str(e)}")
        return report

    # Check for duplicate timestamps
    if dates.duplicated().any():
        report["warnings"].append("Dataset contains duplicate timestamps. Combining duplicate rows by mean average.")
        
    # 2. Infer frequency
    freq = pd.infer_freq(dates)
    if not freq:
        # Fallback: calculate median time delta between rows
        deltas = dates.diff().dropna()
        if not deltas.empty:
            median_delta = deltas.median()
            days = median_delta.days
            seconds = median_delta.seconds
            
            if days >= 360:
                freq = "YE"
            elif days >= 28:
                freq = "ME"
            elif days >= 7:
                freq = "W"
            elif days >= 1:
                freq = "D"
            elif seconds >= 3600:
                freq = "h"
            elif seconds >= 60:
                freq = "min"
            else:
                freq = "s"
                
    report["frequency"] = freq
    
    # 3. Detect missing timestamps (gaps)
    if freq:
        try:
            ideal_range = pd.date_range(start=dates.min(), end=dates.max(), freq=freq)
            missing_count = max(0, len(ideal_range) - len(dates.unique()))
            report["missingTimestampsCount"] = missing_count
            if missing_count > 0:
                pct_missing = (missing_count / len(ideal_range)) * 100
                report["warnings"].append(f"Detected {missing_count} missing timestamps ({pct_missing:.1f}% gaps) in the series.")
        except Exception:
            pass
            
    # 4. Target candidates (numeric columns)
    target_candidates = []
    for col in df.columns:
        if col != datetime_col and pd.api.types.is_numeric_dtype(df[col]):
            # Verify it's not constant
            if df[col].nunique() > 1:
                target_candidates.append(col)
                
    report["targetCandidates"] = target_candidates
    
    if not target_candidates:
        report["warnings"].append("No numeric target column is available for forecasting.")
        return report
        
    # Set default/suggested target: first numeric column
    # If there's 'sales', 'revenue', 'count', 'demand', 'temperature', suggest it first
    common_targets = ["sales", "revenue", "count", "demand", "temp", "value", "price", "amount"]
    suggested = None
    for c in target_candidates:
        if any(term in c.lower() for term in common_targets):
            suggested = c
            break
    if not suggested:
        suggested = target_candidates[0]
        
    report["suggestedTarget"] = suggested
    report["isFeasible"] = True
    
    return report
