import time
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.neighbors import KNeighborsClassifier
from sklearn.base import BaseEstimator, ClusterMixin

from backend.app.ml.pipelines.builder import build_preprocessing_pipeline
from backend.app.ml.evaluation.metrics import evaluate_clustering, get_clustering_visuals

class PredictiveClusterModel(BaseEstimator, ClusterMixin):
    """
    Wrapper that makes DBSCAN and AgglomerativeClustering predictive for new inputs
    by fitting a KNN classifier on the generated cluster labels.
    """
    def __init__(self, cluster_model, random_state: int = 42):
        self.cluster_model = cluster_model
        self.random_state = random_state
        self.knn = None
        self.labels_ = None
        
    def fit(self, X, y=None):
        # Handle case of empty/nearly empty arrays
        if len(X) == 0:
            self.labels_ = np.array([])
            return self
            
        # Fit the actual clustering model to assign initial cluster labels
        if hasattr(self.cluster_model, "fit_predict"):
            self.labels_ = self.cluster_model.fit_predict(X)
        else:
            self.cluster_model.fit(X)
            self.labels_ = self.cluster_model.labels_
            
        # Train a K-Nearest Neighbors classifier on the preprocessed coordinates
        # to map new predictions to the nearest cluster.
        k = min(5, len(X))
        if k > 0:
            self.knn = KNeighborsClassifier(n_neighbors=k)
            self.knn.fit(X, self.labels_)
        return self
        
    def predict(self, X):
        if self.knn is not None:
            return self.knn.predict(X)
        # Fallback if KNN isn't fitted
        return np.zeros(len(X), dtype=int)

def train_clustering_model(
    df: pd.DataFrame,
    features: list,
    algorithm: str,
    hyperparameters: dict,
    random_state: int,
    numerical_cols: list,
    categorical_cols: list
) -> Tuple[Pipeline, Dict[str, Any], Dict[str, Any], float]:
    """
    Train and evaluate a clustering model. Returns fitted pipeline, metrics, visuals, and training time.
    """
    X = df[features]
    
    # 1. Build Preprocessor
    preprocessor = build_preprocessing_pipeline(
        df, features, numerical_cols, categorical_cols
    )
    
    # 2. Instantiate Clustering algorithm
    if algorithm == "kmeans":
        raw_model = KMeans(random_state=random_state, **hyperparameters)
        # KMeans has a native predict() method, so we can use it directly
        model = raw_model
    elif algorithm == "dbscan":
        raw_model = DBSCAN(**hyperparameters)
        model = PredictiveClusterModel(raw_model, random_state=random_state)
    elif algorithm == "hierarchical":
        raw_model = AgglomerativeClustering(**hyperparameters)
        model = PredictiveClusterModel(raw_model, random_state=random_state)
    else:
        raise ValueError(f"Unknown clustering algorithm: {algorithm}")
        
    # 3. Create pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', model)
    ])
    
    # Fit model and measure time
    start_time = time.time()
    pipeline.fit(X)
    training_time = float(time.time() - start_time)
    
    # 4. Extract generated labels
    # Preprocess X to get numerical coordinates for evaluations
    X_preprocessed = preprocessor.transform(X)
    
    if algorithm == "kmeans":
        labels = pipeline.named_steps['model'].labels_
        # Inertia for KMeans
        inertia = float(pipeline.named_steps['model'].inertia_)
    else:
        labels = pipeline.named_steps['model'].labels_
        inertia = None
        
    # Calculate performance metrics
    metrics = evaluate_clustering(X_preprocessed, labels)
    if inertia is not None:
        metrics["inertia"] = inertia
        
    # Calculate visualization coordinates (PCA 2D scatter coordinates)
    visuals = get_clustering_visuals(X_preprocessed, labels)
    
    return pipeline, metrics, visuals, training_time
