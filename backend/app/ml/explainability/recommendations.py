import pandas as pd
import numpy as np
from typing import List, Dict, Any

def generate_business_recommendations(
    df: pd.DataFrame,
    features: List[str],
    feature_importances: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate deterministic business recommendations based on feature importances, correlations, and spreads.
    """
    recommendations = []
    
    # 1. Identify strongest and weakest predictive features
    sorted_features = sorted(feature_importances, key=lambda x: x.get("importance", 0.0), reverse=True)
    
    strongest = [f["feature"] for f in sorted_features[:3] if f.get("importance", 0.0) > 0]
    weakest = [f["feature"] for f in sorted_features[-3:] if f.get("importance", 0.0) <= 0.05]
    
    if strongest:
        recommendations.append({
            "category": "strength",
            "title": "Strongest Predictors",
            "description": f"Features {', '.join([f'`{s}`' for s in strongest])} have the highest contribution to the model's predictions. Focus on optimizing data collection quality for these columns."
        })
        
    if weakest:
        recommendations.append({
            "category": "removal",
            "title": "Weakest Predictors",
            "description": f"Features {', '.join([f'`{w}`' for w in weakest])} have negligible impact on predictions. You can safely remove them in the next training cycle to simplify model complexity and speed up training."
        })
        
    # 2. Multicollinearity analysis
    numeric_features = [f for f in features if f in df.columns and pd.api.types.is_numeric_dtype(df[f])]
    if len(numeric_features) > 1:
        corr_matrix = df[numeric_features].corr(method="pearson").abs()
        
        collinear_pairs = []
        for i in range(len(numeric_features)):
            for j in range(i + 1, len(numeric_features)):
                col1 = numeric_features[i]
                col2 = numeric_features[j]
                val = corr_matrix.loc[col1, col2]
                if val > 0.85:
                    collinear_pairs.append((col1, col2, val))
                    
        for col1, col2, val in collinear_pairs:
            recommendations.append({
                "category": "multicollinearity",
                "title": "Multicollinearity Alert",
                "description": f"Features `{col1}` and `{col2}` are highly correlated (Pearson Correlation = {val:.2f}). This can inflate model error rates or coefficients. Suggest keeping only one of them."
            })
            
    # 3. Feature engineering recommendations (skewness and datetime features)
    for col in features:
        if col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Check for skewness
                skew = df[col].skew()
                if abs(skew) > 1.5:
                    recommendations.append({
                        "category": "engineering",
                        "title": "Logarithmic Transformation Opportunity",
                        "description": f"Column `{col}` has high statistical skewness ({skew:.2f}). Applying a Logarithmic transformation (`np.log1p`) can help linear and distance-based estimators converge faster."
                    })
            # Check for datetime columns left in features list
            if pd.api.types.is_datetime64_any_dtype(df[col]) or "date" in col.lower() or "time" in col.lower():
                recommendations.append({
                    "category": "engineering",
                    "title": "Date Part Feature Extraction",
                    "description": f"Feature `{col}` appears to contain datetime information. Extracting structured attributes like `day_of_week`, `month`, or `hour` will provide much richer signals to the estimators than raw date strings."
                })
                
    # If no specific recommendations generated
    if not recommendations:
        recommendations.append({
            "category": "info",
            "title": "Optimal Configuration",
            "description": "No immediate warnings or redundant features detected. The current model configuration is stable and aligned with dataset features."
        })
        
    return {
        "strongestFeatures": strongest,
        "weakestFeatures": weakest,
        "recommendations": recommendations
    }
