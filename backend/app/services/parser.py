import os
import pandas as pd
from typing import Dict, Any

def parse_file_metadata(file_path: str, file_extension: str) -> Dict[str, Any]:
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read data based on extension
    if file_extension.lower() == ".csv":
        df = pd.read_csv(file_path)
    elif file_extension.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path, engine="openpyxl")
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

    # Calculate statistics
    rows = len(df)
    columns = len(df.columns)
    missing_values = int(df.isnull().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    size_bytes = os.path.getsize(file_path)

    # Classify columns
    numerical_cols = []
    categorical_cols = []
    date_cols = []
    column_types = {}

    for col in df.columns:
        # Check if object column should be parsed as datetime
        if df[col].dtype == 'object':
            col_lower = str(col).lower()
            if 'date' in col_lower or 'time' in col_lower or 'timestamp' in col_lower:
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

        # Identify type
        if pd.api.types.is_numeric_dtype(df[col].dtype):
            numerical_cols.append(str(col))
            column_types[str(col)] = "numerical"
        elif pd.api.types.is_datetime64_any_dtype(df[col].dtype):
            date_cols.append(str(col))
            column_types[str(col)] = "datetime"
        else:
            categorical_cols.append(str(col))
            column_types[str(col)] = "categorical"

    return {
        "rows": rows,
        "columns": columns,
        "missingValues": missing_values,
        "duplicateRows": duplicate_rows,
        "size": size_bytes,
        "columnTypes": column_types,
        "numericalColumns": numerical_cols,
        "categoricalColumns": categorical_cols,
        "dateColumns": date_cols
    }
