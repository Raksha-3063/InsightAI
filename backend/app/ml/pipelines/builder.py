import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, OneHotEncoder, OrdinalEncoder

def build_preprocessing_pipeline(
    df: pd.DataFrame, 
    features: list, 
    numerical_cols: list, 
    categorical_cols: list, 
    scaling_method: str = "standard", 
    encoding_method: str = "onehot"
) -> ColumnTransformer:
    """
    Build a scikit-learn ColumnTransformer for preprocessing features.
    """
    # Build numerical transformer pipeline
    num_steps = [('imputer', SimpleImputer(strategy='median'))]
    
    if scaling_method == "standard":
        num_steps.append(('scaler', StandardScaler()))
    elif scaling_method == "minmax":
        num_steps.append(('scaler', MinMaxScaler()))
    elif scaling_method == "robust":
        num_steps.append(('scaler', RobustScaler()))
        
    num_pipeline = Pipeline(num_steps)
    
    # Build categorical transformer pipeline
    cat_steps = [('imputer', SimpleImputer(strategy='most_frequent'))]
    
    if encoding_method == "onehot":
        cat_steps.append(('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False)))
    elif encoding_method == "ordinal":
        cat_steps.append(('encoder', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)))
        
    cat_pipeline = Pipeline(cat_steps)
    
    # Filter features into numerical and categorical based on classifications
    valid_num_cols = [c for c in numerical_cols if c in features and c in df.columns]
    valid_cat_cols = [c for c in categorical_cols if c in features and c in df.columns]
    
    transformers = []
    if valid_num_cols:
        transformers.append(('num', num_pipeline, valid_num_cols))
    if valid_cat_cols:
        transformers.append(('cat', cat_pipeline, valid_cat_cols))
        
    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder='drop'
    )
    
    return preprocessor
