import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_curve, auc, silhouette_score, davies_bouldin_score
)
from sklearn.decomposition import PCA
from backend.app.ml.statistics.service import clean_float

def evaluate_regression(y_true: Any, y_pred: Any) -> Dict[str, Any]:
    """
    Calculate regression performance metrics.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)
    
    return {
        "mae": clean_float(mae),
        "mse": clean_float(mse),
        "rmse": clean_float(rmse),
        "r2": clean_float(r2)
    }

def get_regression_visuals(y_true: Any, y_pred: Any, max_points: int = 500) -> Dict[str, Any]:
    """
    Generate coordinates for Regression performance plots.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    # Downsample points for performance
    indices = np.arange(len(y_true))
    if len(y_true) > max_points:
        np.random.seed(42)
        indices = np.random.choice(indices, size=max_points, replace=False)
        
    actuals = y_true[indices]
    preds = y_pred[indices]
    residuals = actuals - preds
    
    actual_vs_predicted = [
        {"actual": clean_float(act), "predicted": clean_float(pred)} 
        for act, pred in zip(actuals, preds)
    ]
    
    residual_plot = [
        {"predicted": clean_float(pred), "residual": clean_float(res)}
        for pred, res in zip(preds, residuals)
    ]
    
    # Calculate error distribution histogram
    counts, edges = np.histogram(residuals, bins=15)
    error_distribution = []
    for i in range(len(counts)):
        label = f"{clean_float(edges[i]):.2f} - {clean_float(edges[i+1]):.2f}"
        error_distribution.append({
            "binName": label,
            "count": int(counts[i]),
            "min": clean_float(edges[i]),
            "max": clean_float(edges[i+1])
        })
        
    return {
        "actualVsPredicted": actual_vs_predicted,
        "residualPlot": residual_plot,
        "errorDistribution": error_distribution
    }

def evaluate_classification(y_true: Any, y_pred: Any, y_prob: Any = None) -> Dict[str, Any]:
    """
    Calculate classification performance metrics.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if y_prob is not None:
        y_prob = np.asarray(y_prob)
    # Auto-detect if multi-class
    unique_classes = np.unique(y_true)
    is_multiclass = len(unique_classes) > 2
    average_method = "macro" if is_multiclass else "binary"
    
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average=average_method, zero_division=0)
    recall = recall_score(y_true, y_pred, average=average_method, zero_division=0)
    f1 = f1_score(y_true, y_pred, average=average_method, zero_division=0)
    
    # ROC AUC calculation
    roc_auc = None
    if y_prob is not None:
        try:
            if is_multiclass:
                # multiclass ROC AUC
                from sklearn.metrics import roc_auc_score
                roc_auc = roc_auc_score(y_true, y_prob, multi_class='ovr', average='macro')
            else:
                from sklearn.metrics import roc_auc_score
                # binary classification probability is typically the second column
                prob_col = y_prob[:, 1] if y_prob.ndim > 1 else y_prob
                roc_auc = roc_auc_score(y_true, prob_col)
        except Exception:
            pass
            
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    cm_list = cm.tolist()
    
    return {
        "accuracy": clean_float(accuracy),
        "precision": clean_float(precision),
        "recall": clean_float(recall),
        "f1": clean_float(f1),
        "rocAuc": clean_float(roc_auc),
        "confusionMatrix": cm_list
    }

def get_classification_visuals(y_true: Any, y_prob: Any) -> Dict[str, Any]:
    """
    Generate coordinates for ROC curve.
    """
    y_true = np.asarray(y_true)
    if y_prob is not None:
        y_prob = np.asarray(y_prob)
    roc_curve_data = []
    
    if y_prob is not None:
        try:
            # We support ROC curve binary plot coordinates
            unique_classes = np.unique(y_true)
            if len(unique_classes) == 2:
                prob_col = y_prob[:, 1] if y_prob.ndim > 1 else y_prob
                fpr, tpr, thresholds = roc_curve(y_true, prob_col)
                
                # Downsample curve coordinates if too long
                step = 1
                if len(fpr) > 100:
                    step = int(len(fpr) / 100)
                
                for idx in range(0, len(fpr), step):
                    roc_curve_data.append({
                        "fpr": clean_float(fpr[idx]),
                        "tpr": clean_float(tpr[idx])
                    })
                # Add final coordinate
                roc_curve_data.append({
                    "fpr": 1.0,
                    "tpr": 1.0
                })
        except Exception:
            pass
            
    return {
        "rocCurve": roc_curve_data
    }

def evaluate_clustering(X: Any, labels: Any) -> Dict[str, Any]:
    """
    Calculate clustering scores.
    """
    X = np.asarray(X)
    labels = np.asarray(labels)
    unique_labels = np.unique(labels)
    n_clusters = len(unique_labels)
    
    # If all noise (e.g. DBSCAN labels are all -1) or single cluster
    if n_clusters < 2:
        return {
            "silhouette": None,
            "daviesBouldin": None
        }
        
    try:
        silhouette = silhouette_score(X, labels)
    except Exception:
        silhouette = None
        
    try:
        db_score = davies_bouldin_score(X, labels)
    except Exception:
        db_score = None
        
    return {
        "silhouette": clean_float(silhouette),
        "daviesBouldin": clean_float(db_score)
    }

def get_clustering_visuals(X: Any, labels: Any, max_points: int = 500) -> Dict[str, Any]:
    """
    Reduce features X to 2D using PCA, returning PCA coordinates with cluster labels.
    """
    X = np.asarray(X)
    labels = np.asarray(labels)
    # Downsample points for PCA plotting to avoid performance issues
    indices = np.arange(len(X))
    if len(X) > max_points:
        np.random.seed(42)
        indices = np.random.choice(indices, size=max_points, replace=False)
        
    X_sample = X[indices]
    labels_sample = labels[indices]
    
    cluster_plot = []
    
    if len(X_sample) > 0:
        try:
            # PCA downscaling to 2 dimensions
            pca = PCA(n_components=2, random_state=42)
            X_2d = pca.fit_transform(X_sample)
            
            for i in range(len(X_2d)):
                cluster_plot.append({
                    "x": clean_float(X_2d[i, 0]),
                    "y": clean_float(X_2d[i, 1]),
                    "cluster": int(labels_sample[i])
                })
        except Exception as e:
            print("PCA calculation failed:", e)
            
    # Distribution frequency counts
    freq = {}
    for lbl in labels:
        freq[int(lbl)] = freq.get(int(lbl), 0) + 1
        
    distribution = [{"cluster": k, "count": v} for k, v in freq.items()]
    
    return {
        "clusterScatter": cluster_plot,
        "clusterDistribution": distribution
    }
