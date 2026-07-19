from bson import ObjectId
from typing import Dict, Any, List

async def build_workspace_context(project_id: str, dataset_doc: Dict[str, Any], db: Any) -> Dict[str, Any]:
    """
    Consolidates dataset profile, EDA, cleaning history, ML, and forecast metrics
    into a structured context summary.
    """
    context = {
        "datasetInfo": {
            "fileName": dataset_doc.get("fileName"),
            "rowsCount": dataset_doc.get("rows", 0),
            "columnsCount": dataset_doc.get("columns", 0),
            "missingValues": dataset_doc.get("missingValues", 0),
            "duplicateRows": dataset_doc.get("duplicateRows", 0),
            "columnTypes": dataset_doc.get("columnTypes", {}),
            "numericalColumns": dataset_doc.get("numericalColumns", []),
            "categoricalColumns": dataset_doc.get("categoricalColumns", []),
            "dateColumns": dataset_doc.get("dateColumns", [])
        },
        "cleaningHistory": dataset_doc.get("cleaningHistory", []),
        "healthScore": 100,  # Default fallback
        "correlationsSummary": {},
        "machineLearningModels": [],
        "forecastingModels": []
    }
    
    # 1. Fetch health score & correlations
    health_doc = await db.health_score.find_one({"projectId": project_id})
    if health_doc:
        context["healthScore"] = health_doc.get("score", 100)
        
    corr_doc = await db.correlations.find_one({"projectId": project_id})
    if corr_doc and "matrix" in corr_doc:
        # Save a simplified correlation summary: only pairs with correlation > 0.6
        matrix = corr_doc["matrix"]
        strong_correlations = []
        features = list(matrix.keys())
        for i in range(len(features)):
            for j in range(i + 1, len(features)):
                col1 = features[i]
                col2 = features[j]
                val = matrix[col1].get(col2, 0.0)
                if abs(val) > 0.6:
                    strong_correlations.append({
                        "featureA": col1,
                        "featureB": col2,
                        "coefficient": val
                    })
        context["correlationsSummary"] = strong_correlations
        
    # 2. Fetch ML models in project
    ml_cursor = db.models.find({"projectId": project_id})
    async for ml_doc in ml_cursor:
        context["machineLearningModels"].append({
            "modelId": str(ml_doc["_id"]),
            "modelName": ml_doc.get("modelName"),
            "algorithm": ml_doc.get("algorithm"),
            "taskType": ml_doc.get("taskType"),
            "targetColumn": ml_doc.get("targetColumn"),
            "features": ml_doc.get("features", []),
            "metrics": ml_doc.get("metrics", {}),
            "trainingTime": ml_doc.get("trainingTime"),
            "featureImportance": ml_doc.get("featureImportance", [])[:5]  # Top 5 only
        })
        
    # 3. Fetch forecasting models in project
    fc_cursor = db.forecasts.find({"projectId": project_id})
    async for fc_doc in fc_cursor:
        context["forecastingModels"].append({
            "forecastId": str(fc_doc["_id"]),
            "algorithm": fc_doc.get("algorithm"),
            "targetColumn": fc_doc.get("targetColumn"),
            "dateColumn": fc_doc.get("dateColumn"),
            "horizon": fc_doc.get("horizon"),
            "metrics": fc_doc.get("metrics", {}),
            "createdDate": fc_doc.get("createdDate").strftime("%Y-%m-%d") if fc_doc.get("createdDate") else None
        })
        
    return context
