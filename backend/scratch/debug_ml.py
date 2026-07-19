import pandas as pd
from backend.app.ml.training.regression import train_regression_model

csv_content = (
    "Age,Salary,Target,Label,Group\n"
    "25,50000,1,Yes,A\n"
    "30,60000,0,No,B\n"
    "35,55000,1,Yes,A\n"
    "40,65000,0,No,C\n"
    "45,70000,1,Yes,B\n"
)
from io import StringIO
df = pd.read_csv(StringIO(csv_content))

features = ["Age", "Target"]
target = "Salary"
algorithm = "linear_regression"
hyperparameters = {}
split_ratio = 0.2
random_state = 42
numerical_cols = ["Age", "Salary", "Target"]
categorical_cols = ["Label", "Group"]

try:
    pipeline, metrics, visuals, importance, train_time = train_regression_model(
        df, features, target, algorithm, hyperparameters,
        split_ratio, random_state, numerical_cols, categorical_cols
    )
    print("Success! Metrics:", metrics)
except Exception as e:
    import traceback
    traceback.print_exc()
