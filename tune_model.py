import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, make_scorer
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# 1. Load the cleaned dataset
df = pd.read_csv("data/processed/cleaned_dataset.csv")

# 2. Separate the features (X) and target (y)
# Exclude Student_ID because it is only an identifier.
# Exclude Final_Exam_Score to avoid target leakage.
X = df.drop(columns=["Pass_status", "Student_ID", "Final_Exam_Score"])
y = df["Pass_status"]

# 3. Identify categorical and numerical columns
categorical_columns = X.select_dtypes(
    include=["object", "category", "bool", "str"]
).columns.tolist()

numerical_columns = X.select_dtypes(include=["number"]).columns.tolist()

print("Categorical features:", categorical_columns)
print("Numerical features:", numerical_columns)

# 4. Prepare categorical features
categorical_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ]
)

# 5. Prepare numerical features
numerical_pipeline = Pipeline(
    steps=[("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
)

# 6. Combine the preprocessing steps
preprocessor = ColumnTransformer(
    transformers=[
        ("categorical", categorical_pipeline, categorical_columns),
        ("numerical", numerical_pipeline, numerical_columns),
    ]
)

# 7. Build the complete machine-learning pipeline
pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=2000)),
    ]
)

# 8. Define the settings to test
parameter_grid = {
    "classifier__C": [0.01, 0.1, 1, 10, 100],
    "classifier__class_weight": [None, "balanced"],
}

# 9. Configure five-fold stratified cross-validation
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# 10. Search for the best settings using Pass F1-score
pass_f1_scorer = make_scorer(f1_score, pos_label="Pass")
search = GridSearchCV(
    estimator=pipeline,
    param_grid=parameter_grid,
    scoring=pass_f1_scorer,
    cv=cv,
    refit=True,
    n_jobs=-1,
    return_train_score=False,
    error_score="raise",
)

# 11. Train and evaluate all parameter combinations
print("\nTuning the Logistic Regression model...")
search.fit(X, y)

# 12. Display the best parameters
print("\nBEST PARAMETERS")
print(search.best_params_)

# 13. Display the best mean cross-validation F1-score
print("\nBEST MEAN CROSS-VALIDATION PASS F1-SCORE")
print(round(search.best_score_, 3))

# 14. Display the top 10 parameter combinations
results = pd.DataFrame(search.cv_results_)

results = results.sort_values(by="mean_test_score", ascending=False)

print("\nTOP 10 PARAMETER COMBINATIONS")
print(
    results[
        [
            "param_classifier__C",
            "param_classifier__class_weight",
            "mean_test_score",
            "std_test_score",
        ]
    ]
    .head(10)
    .to_string(index=False)
)

# 15. Save the best model
import os

import joblib

os.makedirs("models", exist_ok=True)

joblib.dump(search.best_estimator_, "models/pass_status_model.pkl")

print("\nBest model saved to models/pass_status_model.pkl")
