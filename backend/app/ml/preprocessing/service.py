import pandas as pd
import numpy as np
from typing import Dict, Any, List

def apply_cleaning_operation(df: pd.DataFrame, op_type: str, params: Dict[str, Any]) -> pd.DataFrame:
    """
    Applies a specific data preprocessing operation to a DataFrame.
    """
    # Create a copy to prevent in-place side effects
    df = df.copy()
    
    if op_type == "impute_missing":
        col = params.get("column")
        strategy = params.get("strategy", "mean")
        
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame.")
            
        if strategy == "mean":
            # Only numeric columns
            if pd.api.types.is_numeric_dtype(df[col].dtype):
                mean_val = df[col].mean()
                df[col] = df[col].fillna(mean_val)
            else:
                raise ValueError(f"Mean imputation is only supported for numerical columns, not {df[col].dtype}.")
        elif strategy == "median":
            if pd.api.types.is_numeric_dtype(df[col].dtype):
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
            else:
                raise ValueError(f"Median imputation is only supported for numerical columns.")
        elif strategy == "mode":
            mode_val_series = df[col].mode()
            if not mode_val_series.empty:
                df[col] = df[col].fillna(mode_val_series[0])
        elif strategy == "ffill":
            df[col] = df[col].ffill()
        elif strategy == "bfill":
            df[col] = df[col].bfill()
        elif strategy == "val":
            fill_val = params.get("fill_value")
            df[col] = df[col].fillna(fill_val)
            
    elif op_type == "drop_missing_rows":
        col = params.get("column")
        if col:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found in DataFrame.")
            df = df.dropna(subset=[col])
        else:
            df = df.dropna()
            
    elif op_type == "drop_column":
        col = params.get("column")
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame.")
        df = df.drop(columns=[col])
        
    elif op_type == "remove_duplicates":
        df = df.drop_duplicates()
        
    elif op_type == "handle_outliers":
        col = params.get("column")
        method = params.get("method", "iqr")  # iqr or zscore
        action = params.get("action", "drop")  # drop or cap
        threshold = float(params.get("threshold", 3.0)) # zscore threshold, or IQR factor (typically 1.5)
        
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame.")
        if not pd.api.types.is_numeric_dtype(df[col].dtype):
            raise ValueError(f"Outlier handling requires numerical column, got {df[col].dtype}.")
            
        non_null_series = df[col].dropna()
        if non_null_series.empty:
            return df
            
        if method == "iqr":
            q1 = non_null_series.quantile(0.25)
            q3 = non_null_series.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            
            if action == "drop":
                df = df[(df[col].isna()) | ((df[col] >= lower_bound) & (df[col] <= upper_bound))]
            elif action == "cap":
                df[col] = np.clip(df[col], lower_bound, upper_bound)
                
        elif method == "zscore":
            mean = non_null_series.mean()
            std = non_null_series.std()
            if std == 0:
                return df
                
            if action == "drop":
                z_scores = np.abs((df[col] - mean) / std)
                df = df[(df[col].isna()) | (z_scores <= threshold)]
            elif action == "cap":
                lower_bound = mean - threshold * std
                upper_bound = mean + threshold * std
                df[col] = np.clip(df[col], lower_bound, upper_bound)

    elif op_type == "encode_column":
        col = params.get("column")
        method = params.get("method", "label") # label, onehot, ordinal
        
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame.")
            
        if method == "label":
            # Factorize string categories into numbers
            df[col] = pd.factorize(df[col])[0]
            
        elif method == "onehot":
            # Generate dummy variables and append, then drop original column
            dummies = pd.get_dummies(df[col], prefix=col, dtype=int)
            df = pd.concat([df, dummies], axis=1)
            df = df.drop(columns=[col])
            
        elif method == "ordinal":
            order = params.get("order") # List of categories in order
            if not order:
                raise ValueError("Ordinal encoding requires 'order' list of values.")
            mapping = {val: i for i, val in enumerate(order)}
            # Map values, default unmapped values to NaN or -1
            df[col] = df[col].map(mapping).fillna(-1).astype(int)

    elif op_type == "scale_column":
        col = params.get("column")
        method = params.get("method", "standard") # standard, minmax, robust
        
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame.")
        if not pd.api.types.is_numeric_dtype(df[col].dtype):
            raise ValueError(f"Scaling requires numerical column, got {df[col].dtype}.")
            
        non_null_series = df[col].dropna()
        if non_null_series.empty:
            return df
            
        if method == "standard":
            mean = non_null_series.mean()
            std = non_null_series.std()
            if std > 0:
                df[col] = (df[col] - mean) / std
        elif method == "minmax":
            val_min = non_null_series.min()
            val_max = non_null_series.max()
            diff = val_max - val_min
            if diff > 0:
                df[col] = (df[col] - val_min) / diff
        elif method == "robust":
            q1 = non_null_series.quantile(0.25)
            q3 = non_null_series.quantile(0.75)
            median = non_null_series.median()
            iqr = q3 - q1
            if iqr > 0:
                df[col] = (df[col] - median) / iqr

    return df
