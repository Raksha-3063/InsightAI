import os
import pandas as pd
from typing import List, Dict, Any, Tuple

def predict_manual(
    pipeline: Any, 
    features: List[str], 
    input_data: List[Dict[str, Any]], 
    target_encoder: Any = None
) -> List[Any]:
    """
    Run predictions on manually input feature values.
    """
    df = pd.DataFrame(input_data)
    
    # Reindex columns to match the trained features list, filling missing columns with NaN
    df = df.reindex(columns=features)
    
    # Run prediction pipeline
    preds = pipeline.predict(df)
    
    # Decode target label predictions if LabelEncoder is provided (classification)
    if target_encoder is not None:
        try:
            preds = target_encoder.inverse_transform(preds)
        except Exception:
            pass
            
    return preds.tolist()

def predict_batch(
    pipeline: Any, 
    features: List[str], 
    file_path: str, 
    target_encoder: Any = None
) -> Tuple[pd.DataFrame, str]:
    """
    Load a CSV/Excel dataset, generate predictions, append them as a column, and save the result.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Batch file not found: {file_path}")
        
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext == ".csv":
        df = pd.read_csv(file_path)
    elif file_ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path, engine="openpyxl")
    else:
        raise ValueError(f"Unsupported batch file format: {file_ext}")
        
    # Reindex a copy of the dataframe to feed into the prediction pipeline
    df_features = df.reindex(columns=features)
    
    # Generate predictions
    preds = pipeline.predict(df_features)
    
    # Decode if classification target
    if target_encoder is not None:
        try:
            preds = target_encoder.inverse_transform(preds)
        except Exception:
            pass
            
    # Add predictions as a new column to the original DataFrame
    df["Prediction"] = preds.tolist()
    
    # Save the predicted DataFrame to a new file in same directory
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    pred_filename = f"predicted_{base_name}"
    pred_file_path = os.path.join(dir_name, pred_filename)
    
    if file_ext == ".csv":
        df.to_csv(pred_file_path, index=False)
    else:
        df.to_excel(pred_file_path, index=False, engine="openpyxl")
        
    return df, pred_file_path
