import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, make_scorer, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# 1. Load the cleaned dataset
df = pd.read_csv("data/processed/cleaned_dataset.csv")

# 2. Use all seven features
X = df.drop(columns=["Pass_status", "Student_ID", "Final_Exam_Score"])
y = df["Pass_status"]

print("Features used:")
print(X.columns.tolist())

# 3. Identify categorical and numerical features
categorical_columns = X.select_dtypes(
    include=["object", "category", "bool", "str"]
).columns.tolist()

numerical_columns = X.select_dtypes(include=["number"]).columns.tolist()

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

# 6. Combine preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ("categorical", categorical_pipeline, categorical_columns),
        ("numerical", numerical_pipeline, numerical_columns),
    ]
)

# 7. Build Logistic Regression
model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000)),
    ]
)

# 8. Define five stratified folds
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# 9. Define evaluation metrics
scoring = {
    "accuracy": "accuracy",
    "pass_recall": make_scorer(recall_score, pos_label="Pass", zero_division=0),
    "pass_precision": make_scorer(precision_score, pos_label="Pass", zero_division=0),
    "pass_f1": make_scorer(f1_score, pos_label="Pass", zero_division=0),
}

# 10. Run cross-validation
results = cross_validate(model, X, y, cv=cv, scoring=scoring)

# 11. Display results
print("\nFive-fold cross-validation results:")

for metric in scoring:
    scores = results[f"test_{metric}"]

    print(f"{metric}: {scores.mean():.3f} +/- {scores.std():.3f}")
