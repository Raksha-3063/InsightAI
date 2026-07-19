import os
import pandas as pd
from typing import Dict, Any, List

def profile_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Profile a Pandas DataFrame to extract metadata, statistics, and column classifications.
    """
    rows, columns = df.shape
    
    # Calculate memory usage in bytes
    memory_usage = int(df.memory_usage(deep=True).sum())
    
    # Calculate duplicate rows
    duplicate_rows = int(df.duplicated().sum())
    
    # Missing value analysis
    missing_by_col = df.isnull().sum()
    total_missing = int(missing_by_col.sum())
    
    # Data type analysis
    data_types = {str(col): str(dtype) for col, dtype in df.dtypes.items()}
    
    # Classify columns
    numerical_cols = []
    categorical_cols = []
    boolean_cols = []
    datetime_cols = []
    text_cols = []
    column_types = {}
    
    null_counts = {str(col): int(count) for col, count in missing_by_col.items()}
    null_percentages = {str(col): float((count / rows) * 100) if rows > 0 else 0.0 for col, count in missing_by_col.items()}

    for col in df.columns:
        col_str = str(col)
        # 1. Check if datetime
        if pd.api.types.is_datetime64_any_dtype(df[col].dtype):
            datetime_cols.append(col_str)
            column_types[col_str] = "datetime"
            continue
            
        # Try converting object columns that look like date to datetime
        if df[col].dtype == 'object' or df[col].dtype == 'string':
            col_lower = col_str.lower()
            if 'date' in col_lower or 'time' in col_lower or 'timestamp' in col_lower:
                try:
                    parsed_date = pd.to_datetime(df[col], errors='raise')
                    df[col] = parsed_date
                    datetime_cols.append(col_str)
                    column_types[col_str] = "datetime"
                    continue
                except Exception:
                    pass

        # 2. Check if boolean
        if pd.api.types.is_bool_dtype(df[col].dtype):
            boolean_cols.append(col_str)
            column_types[col_str] = "boolean"
            continue
            
        # Check if column has exactly 2 unique values and looks like boolean
        non_null_series = df[col].dropna()
        unique_vals = non_null_series.unique()
        if len(unique_vals) == 2:
            unique_set = set(str(v).lower() for v in unique_vals)
            if unique_set.issubset({"true", "false", "0", "1", "0.0", "1.0", "yes", "no", "y", "n"}):
                boolean_cols.append(col_str)
                column_types[col_str] = "boolean"
                continue

        # 3. Check if numerical
        if pd.api.types.is_numeric_dtype(df[col].dtype):
            numerical_cols.append(col_str)
            column_types[col_str] = "numerical"
            continue

        # 4. Check if categorical or text
        # If cardinality is low, classify as categorical; otherwise text
        cardinality = len(unique_vals)
        if cardinality < 20 or (rows > 0 and cardinality / rows < 0.05):
            categorical_cols.append(col_str)
            column_types[col_str] = "categorical"
        else:
            text_cols.append(col_str)
            column_types[col_str] = "text"

    # Target Column Suggestion
    target_suggestion = None
    # Look for common names first
    target_keywords = ["target", "label", "price", "class", "outcome", "revenue", "sales", "churn", "status"]
    for keyword in target_keywords:
        for col in df.columns:
            if keyword in str(col).lower():
                target_suggestion = str(col)
                break
        if target_suggestion:
            break
            
    # Fallback to the last column if no keyword matches
    if not target_suggestion and len(df.columns) > 0:
        target_suggestion = str(df.columns[-1])

    return {
        "rows": rows,
        "columns": columns,
        "memoryUsage": memory_usage,
        "missingValues": total_missing,
        "duplicateRows": duplicate_rows,
        "columnTypes": column_types,
        "numericalColumns": numerical_cols,
        "categoricalColumns": categorical_cols,
        "booleanColumns": boolean_cols,
        "dateColumns": datetime_cols,
        "textColumns": text_cols,
        "targetSuggestion": target_suggestion,
        "nullCounts": null_counts,
        "nullPercentages": null_percentages,
        "dataTypes": data_types
    }
