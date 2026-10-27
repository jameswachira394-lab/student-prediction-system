import os

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    make_scorer,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# 1. Load the cleaned dataset
df = pd.read_csv("data/processed/cleaned_dataset.csv")

# 2. Separate features and target
# Exclude the ID and Final_Exam_Score to prevent leakage.
X = df.drop(columns=["Pass_status", "Student_ID", "Final_Exam_Score"])
y = df["Pass_status"]

# 3. Split the data BEFORE tuning
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print("Training records:", len(X_train))
print("Testing records:", len(X_test))

# 4. Identify categorical and numerical features
categorical_columns = X.select_dtypes(
    include=["object", "category", "bool", "str"]
).columns.tolist()

numerical_columns = X.select_dtypes(include=["number"]).columns.tolist()

print("\nCategorical features:", categorical_columns)
print("Numerical features:", numerical_columns)

# 5. Preprocess categorical features
categorical_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ]
)

# 6. Preprocess numerical features
numerical_pipeline = Pipeline(
    steps=[("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
)

# 7. Combine preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ("categorical", categorical_pipeline, categorical_columns),
        ("numerical", numerical_pipeline, numerical_columns),
    ]
)

# 8. Build the model pipeline
pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=2000)),
    ]
)

# 9. Define the hyperparameters to test
parameter_grid = {
    "classifier__C": [0.01, 0.1, 1, 10, 100],
    "classifier__class_weight": [None, "balanced"],
}

# 10. Configure cross-validation on TRAINING data only
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

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

# 11. Tune using the training data only
print("\nTuning the model using training data...")
search.fit(X_train, y_train)

print("\nBEST PARAMETERS")
print(search.best_params_)

print("\nBEST TRAINING CROSS-VALIDATION PASS F1-SCORE")
print(round(search.best_score_, 3))

# 12. Evaluate on the untouched test set
best_model = search.best_estimator_
y_pred = best_model.predict(X_test)

print("\nTEST SET ACCURACY")
print(round(accuracy_score(y_test, y_pred), 3))

print("\nTEST SET CLASSIFICATION REPORT")
print(classification_report(y_test, y_pred, labels=["Fail", "Pass"], zero_division=0))

# 13. Display the confusion matrix
cm = confusion_matrix(y_test, y_pred, labels=["Fail", "Pass"])

print("\nCONFUSION MATRIX")
print(
    pd.DataFrame(
        cm,
        index=["Actual Fail", "Actual Pass"],
        columns=["Predicted Fail", "Predicted Pass"],
    )
)

# 14. Plot the confusion matrix
display = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Fail", "Pass"])
display.plot()
plt.title("Logistic Regression - Test Set")
plt.tight_layout()
plt.show()

# 15. Save the evaluated model
os.makedirs("models", exist_ok=True)

joblib.dump(best_model, "models/pass_status_model.pkl")

print("\nBest model saved to models/pass_status_model.pkl")
