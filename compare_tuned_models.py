
import os
import joblib
import pandas as pd

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    GridSearchCV
)
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    make_scorer
)

# 1. Load the dataset
df = pd.read_csv("data/processed/cleaned_dataset.csv")

# 2. Separate features and target
X = df.drop(
    columns=["Pass_status", "Student_ID", "Final_Exam_Score"]
)
y = df["Pass_status"]

# 3. Create the same train/test split as before
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training records:", len(X_train))
print("Testing records:", len(X_test))

# 4. Identify feature types
categorical_columns = X.select_dtypes(
    include=["object", "category", "bool", "str"]
).columns.tolist()

numerical_columns = X.select_dtypes(
    include=["number"]
).columns.tolist()

# 5. Build preprocessing pipelines
categorical_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

numerical_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

preprocessor = ColumnTransformer(transformers=[
    ("categorical", categorical_pipeline, categorical_columns),
    ("numerical", numerical_pipeline, numerical_columns)
])

# 6. Define both model pipelines
logistic_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(max_iter=2000))
])

forest_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(
        random_state=42,
        n_jobs=1
    ))
])

# 7. Define hyperparameter combinations
logistic_grid = {
    "classifier__C": [0.01, 0.1, 1, 10, 100],
    "classifier__class_weight": [None, "balanced"]
}

forest_grid = {
    "classifier__n_estimators": [100, 200],
    "classifier__max_depth": [None, 5, 10],
    "classifier__min_samples_leaf": [1, 2, 5],
    "classifier__class_weight": [None, "balanced"]
}

# 8. Use stratified cross-validation on training data only
cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

pass_f1_scorer = make_scorer(
    f1_score,
    pos_label="Pass"
)

# 9. Tune Logistic Regression
print("\nTUNING LOGISTIC REGRESSION...")

logistic_search = GridSearchCV(
    estimator=logistic_pipeline,
    param_grid=logistic_grid,
    scoring=pass_f1_scorer,
    cv=cv,
    refit=True,
    n_jobs=-1,
    error_score="raise"
)

logistic_search.fit(X_train, y_train)

print("Best parameters:", logistic_search.best_params_)
print(
    "Best training CV Pass F1:",
    round(logistic_search.best_score_, 3)
)

# 10. Tune Random Forest
print("\nTUNING RANDOM FOREST...")

forest_search = GridSearchCV(
    estimator=forest_pipeline,
    param_grid=forest_grid,
    scoring=pass_f1_scorer,
    cv=cv,
    refit=True,
    n_jobs=-1,
    error_score="raise"
)

forest_search.fit(X_train, y_train)

print("Best parameters:", forest_search.best_params_)
print(
    "Best training CV Pass F1:",
    round(forest_search.best_score_, 3)
)

# 11. Evaluate both models on the SAME untouched test set
models = {
    "Logistic Regression": logistic_search,
    "Random Forest": forest_search
}

results = []
best_model_search = None
best_cv_score = float("-inf")

for model_name, search in models.items():
    predictions = search.best_estimator_.predict(X_test)

    results.append({
        "Model": model_name,
        "CV Pass F1": search.best_score_,
        "Test Accuracy": accuracy_score(y_test, predictions),
        "Pass Precision": precision_score(
            y_test, predictions,
            pos_label="Pass", zero_division=0
        ),
        "Pass Recall": recall_score(
            y_test, predictions,
            pos_label="Pass", zero_division=0
        ),
        "Pass F1": f1_score(
            y_test, predictions,
            pos_label="Pass", zero_division=0
        )
    })

    print(f"\n{'=' * 45}")
    print(model_name.upper())
    print("=" * 45)
    print(classification_report(
        y_test,
        predictions,
        labels=["Fail", "Pass"],
        zero_division=0
    ))

    # Select using training cross-validation, not test performance
    if search.best_score_ > best_cv_score:
        best_cv_score = search.best_score_
        best_model_search = search
        best_model_name = model_name

# 12. Display a comparison table
comparison = pd.DataFrame(results)

print("\nMODEL COMPARISON")
print(comparison.round(3).to_string(index=False))

# 13. Save the model selected by training cross-validation
os.makedirs("models", exist_ok=True)

joblib.dump(
    best_model_search.best_estimator_,
    "models/pass_status_model.pkl"
)

print(f"\nSelected using training CV: {best_model_name}")
print("Saved to models/pass_status_model.pkl")
print("Test results were not used to select the saved model.")
