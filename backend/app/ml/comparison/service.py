from typing import List, Dict, Any, Optional

def compare_models(models: List[Dict[str, Any]], primary_metric: Optional[str] = None) -> Dict[str, Any]:
    """
    Compare performance metrics of multiple trained models and recommend the best one.
    """
    if not models:
        return {
            "comparisonTable": [],
            "bestModelId": None,
            "bestModelName": None,
            "recommendationReason": "No models to compare."
        }
        
    comparison_table = []
    best_model = None
    best_score = -float('inf')
    
    # Auto-detect task type from the first model
    task_type = models[0].get("taskType", "regression")
    
    # Set default primary evaluation metric based on task type
    if not primary_metric:
        if task_type == "regression":
            primary_metric = "r2"
        elif task_type == "classification":
            primary_metric = "f1"
        elif task_type == "clustering":
            primary_metric = "silhouette"
            
    is_error_metric = primary_metric in ["mae", "mse", "rmse", "daviesBouldin"]
    
    best_model = models[0]
    best_score = None
    
    for m in models:
        metrics = m.get("metrics", {})
        score = metrics.get(primary_metric)
        
        comparison_table.append({
            "modelId": str(m["_id"]),
            "modelName": m.get("modelName"),
            "algorithm": m.get("algorithm"),
            "taskType": m.get("taskType"),
            "metrics": metrics,
            "trainingTime": m.get("trainingTime"),
            "score": score
        })
        
        if score is not None:
            score_val = float(score)
            if best_score is None:
                best_score = score_val
                best_model = m
            else:
                if is_error_metric:
                    if score_val < best_score:
                        best_score = score_val
                        best_model = m
                else:
                    if score_val > best_score:
                        best_score = score_val
                        best_model = m

    # Build recommendation reason string
    if best_model:
        best_model_id = str(best_model["_id"])
        best_model_name = best_model.get("modelName")
        algo_name = best_model.get("algorithm").replace('_', ' ').title()
        
        if best_score is not None:
            if is_error_metric:
                reason = f"Model '{best_model_name}' ({algo_name}) is recommended because it achieved the lowest {primary_metric.upper()} score ({best_score:.4f})."
            else:
                reason = f"Model '{best_model_name}' ({algo_name}) is recommended because it achieved the highest {primary_metric.upper()} score ({best_score:.4f})."
        else:
            reason = f"Model '{best_model_name}' ({algo_name}) is recommended as the default option since performance scores could not be calculated."
    else:
        best_model_id = None
        best_model_name = None
        reason = "Unable to determine the best model."
        
    return {
        "comparisonTable": comparison_table,
        "bestModelId": best_model_id,
        "bestModelName": best_model_name,
        "recommendationReason": reason
    }
