from typing import Dict, Any, List
from backend.app.ai.providers.gemini import call_gemini_api
from backend.app.ai.prompts.templates import COPILOT_SYSTEM_INSTRUCTION, format_recommendations_prompt

def generate_ai_recommendations(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate evidence-cased optimization recommendation cards.
    """
    # Ask Gemini for structured recommendations
    prompt = format_recommendations_prompt(context)
    llm_output = call_gemini_api(prompt, system_instruction=COPILOT_SYSTEM_INSTRUCTION)
    
    # We will also inject structured deterministic fallback items directly based on context numbers
    cards = []
    
    # 1. Evaluate Health Score
    health = context.get("healthScore", 100)
    if health < 85:
        cards.append({
            "category": "Data Quality",
            "title": "Low Dataset Health Score",
            "description": f"The dataset health score is currently {health}%. Check missing values or duplicates and apply clean operations to improve score.",
            "evidence": f"Health Score = {health}%",
            "confidence": 0.95
        })
    else:
        cards.append({
            "category": "Data Quality",
            "title": "Healthy Dataset Profile",
            "description": "Your dataset health score is in the optimal range. The column catalog is clean and ready for modeling.",
            "evidence": f"Health Score = {health}%",
            "confidence": 0.90
        })
        
    # 2. Evaluate strong correlations
    corrs = context.get("correlationsSummary", [])
    if corrs:
        high_corr = [c for c in corrs if abs(c["coefficient"]) > 0.85]
        if high_corr:
            pair = high_corr[0]
            cards.append({
                "category": "Feature Engineering",
                "title": "Multicollinearity Redundancy",
                "description": f"Features `{pair['featureA']}` and `{pair['featureB']}` are strongly correlated. Remove one feature to prevent model parameters inflation.",
                "evidence": f"Pearson Correlation = {pair['coefficient']:.3f}",
                "confidence": 0.98
            })
            
    # 3. Model performance review
    models = context.get("machineLearningModels", [])
    if len(models) > 1:
        # Find best model
        best_model = None
        best_score = -1.0
        for m in models:
            # check accuracy or f1 or r2
            metrics = m.get("metrics", {})
            score = metrics.get("accuracy") or metrics.get("f1_score") or metrics.get("r2") or 0.0
            if score > best_score:
                best_score = score
                best_model = m
                
        if best_model:
            cards.append({
                "category": "Model Performance",
                "title": "Optimal Classifier Recommended",
                "description": f"Pipeline `{best_model['modelName']}` trained with `{best_model['algorithm']}` shows the highest metric score of {best_score:.4f}.",
                "evidence": f"Metric Score = {best_score:.4f}",
                "confidence": 0.92
            })
            
    # If LLM returned text, summarize it inside a card as well
    if llm_output:
        # Add LLM reasoning summary card
        snippet = llm_output[:250] + "..." if len(llm_output) > 250 else llm_output
        cards.append({
            "category": "AI Copilot Suggestion",
            "title": "Copilot Optimization Strategy",
            "description": snippet.replace("\n", " "),
            "evidence": "Gemini Reasoning Vector",
            "confidence": 0.85
        })
        
    return cards
