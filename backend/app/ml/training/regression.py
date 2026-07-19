import time
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

from backend.app.ml.pipelines.builder import build_preprocessing_pipeline
from backend.app.ml.evaluation.metrics import evaluate_regression, get_regression_visuals

def get_feature_importances(pipeline: Pipeline, features: list) -> list:
    """
    Extract and sort feature importances or coefficients from a fitted model.
    """
    preprocessor = pipeline.named_steps['preprocessor']
    model = pipeline.named_steps['model']
    
    try:
        # Get one-hot encoded features naming mapping
        feature_names = preprocessor.get_feature_names_out()
    except Exception:
        feature_names = features
        
    importances = {}
    
    # 1. Tree feature importances
    if hasattr(model, 'feature_importances_'):
        imp_scores = model.feature_importances_
        importances = {str(name): float(score) for name, score in zip(feature_names, imp_scores)}
        
    # 2. Linear models coefficients
    elif hasattr(model, 'coef_'):
        coefs = model.coef_
        # In case of 2D coefficients array (e.g. multiclass classification)
        if coefs.ndim > 1:
            coefs = np.mean(np.abs(coefs), axis=0)
        importances = {str(name): float(abs(score)) for name, score in zip(feature_names, coefs)}
        
    # If neither (e.g. some clustering models), return empty list
    if not importances:
        return [{"feature": f, "importance": 0.0} for f in features]
        
    # Sort by importance descending
    sorted_importances = sorted(importances.items(), key=lambda x: x[1], reverse=True)
    return [{"feature": f, "importance": float(score)} for f, score in sorted_importances]

def train_regression_model(
    df: pd.DataFrame,
    features: list,
    target: str,
    algorithm: str,
    hyperparameters: dict,
    split_ratio: float,
    random_state: int,
    numerical_cols: list,
    categorical_cols: list
) -> Tuple[Pipeline, Dict[str, Any], Dict[str, Any], list, float]:
    """
    Train and evaluate a regression model. Returns fitted pipeline, metrics, visuals, feature importance, and training time.
    """
    X = df[features]
    y = df[target]
    
    # Train / Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=split_ratio, random_state=random_state
    )
    
    # Build preprocessor
    preprocessor = build_preprocessing_pipeline(
        df, features, numerical_cols, categorical_cols
    )
    
    # Build estimator model
    if algorithm == "linear_regression":
        model = LinearRegression(**hyperparameters)
    elif algorithm == "ridge":
        model = Ridge(**hyperparameters)
    elif algorithm == "lasso":
        model = Lasso(**hyperparameters)
    elif algorithm == "decision_tree":
        model = DecisionTreeRegressor(random_state=random_state, **hyperparameters)
    elif algorithm == "random_forest":
        model = RandomForestRegressor(random_state=random_state, **hyperparameters)
    elif algorithm == "xgboost":
        model = XGBRegressor(random_state=random_state, **hyperparameters)
    else:
        raise ValueError(f"Unknown regression algorithm: {algorithm}")
        
    # Create unified pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', model)
    ])
    
    # Fit model and measure time
    start_time = time.time()
    pipeline.fit(X_train, y_train)
    training_time = float(time.time() - start_time)
    
    # Predict on test split
    y_pred = pipeline.predict(X_test)
    
    # Calculate performance metrics
    metrics = evaluate_regression(y_test, y_pred)
    
    # Calculate visualizations coordinates
    visuals = get_regression_visuals(y_test, y_pred)
    
    # Compute feature importance
    importance = get_feature_importances(pipeline, features)
    
    return pipeline, metrics, visuals, importance, training_time
