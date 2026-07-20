import time
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBClassifier

from app.ml.pipelines.builder import build_preprocessing_pipeline
from app.ml.training.regression import get_feature_importances
from app.ml.evaluation.metrics import evaluate_classification, get_classification_visuals

def train_classification_model(
    df: pd.DataFrame,
    features: list,
    target: str,
    algorithm: str,
    hyperparameters: dict,
    split_ratio: float,
    random_state: int,
    stratified: bool,
    numerical_cols: list,
    categorical_cols: list
) -> Tuple[Pipeline, LabelEncoder, Dict[str, Any], Dict[str, Any], list, float]:
    """
    Train and evaluate a classification model. Returns fitted pipeline, label encoder, metrics, visuals, feature importance, and training time.
    """
    X = df[features]
    y = df[target]
    
    # 1. Encode Target classes to integers starting at 0
    target_encoder = LabelEncoder()
    y_encoded = pd.Series(target_encoder.fit_transform(y), index=y.index)
    
    # 2. Train / Test Split (robust fallback for stratified split)
    try:
        if stratified:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=split_ratio, random_state=random_state, stratify=y_encoded
            )
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=split_ratio, random_state=random_state
            )
    except Exception:
        # Fallback to standard split if stratified fails
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=split_ratio, random_state=random_state
        )
        
    # 3. Build Preprocessor
    preprocessor = build_preprocessing_pipeline(
        df, features, numerical_cols, categorical_cols
    )
    
    # 4. Instantiate Model estimator
    if algorithm == "logistic_regression":
        model = LogisticRegression(max_iter=1000, **hyperparameters)
    elif algorithm == "decision_tree":
        model = DecisionTreeClassifier(random_state=random_state, **hyperparameters)
    elif algorithm == "random_forest":
        model = RandomForestClassifier(random_state=random_state, **hyperparameters)
    elif algorithm == "svm":
        model = SVC(probability=True, random_state=random_state, **hyperparameters)
    elif algorithm == "naive_bayes":
        model = GaussianNB(**hyperparameters)
    elif algorithm == "xgboost":
        # XGBoost requires num_class if multi-class
        classes_count = len(target_encoder.classes_)
        if classes_count > 2 and "objective" not in hyperparameters:
            hyperparameters["objective"] = "multi:softprob"
            hyperparameters["num_class"] = classes_count
        model = XGBClassifier(random_state=random_state, eval_metric="mlogloss", **hyperparameters)
    else:
        raise ValueError(f"Unknown classification algorithm: {algorithm}")
        
    # 5. Create pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', model)
    ])
    
    # Fit model and measure training duration
    start_time = time.time()
    pipeline.fit(X_train, y_train)
    training_time = float(time.time() - start_time)
    
    # 6. Predict classes & probabilities
    y_pred = pipeline.predict(X_test)
    y_prob = None
    if hasattr(pipeline, "predict_proba"):
        try:
            y_prob = pipeline.predict_proba(X_test)
        except Exception:
            pass
            
    # Calculate performance metrics
    metrics = evaluate_classification(y_test, y_pred, y_prob)
    
    # Calculate visualizations coordinates (ROC curve coordinates)
    visuals = get_classification_visuals(y_test, y_prob)
    
    # Compute feature importance
    importance = get_feature_importances(pipeline, features)
    
    return pipeline, target_encoder, metrics, visuals, importance, training_time
