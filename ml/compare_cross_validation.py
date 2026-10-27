import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, make_scorer, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

# 1. Load the cleaned dataset
df = pd.read_csv("data/processed/cleaned_dataset.csv")

# 2. Select all seven features
X = df.drop(columns=["Pass_status", "Student_ID", "Final_Exam_Score"])
y = df["Pass_status"]

# 3. Identify feature types
categorical_columns = X.select_dtypes(
    include=["object", "category", "bool", "str"]
).columns.tolist()

numerical_columns = X.select_dtypes(include=["number"]).columns.tolist()

# 4. Preprocessing
categorical_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ]
)

numerical_pipeline = Pipeline(
    steps=[("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("categorical", categorical_pipeline, categorical_columns),
        ("numerical", numerical_pipeline, numerical_columns),
    ]
)

# 5. Define the models
models = {
    "Decision Tree": DecisionTreeClassifier(
        max_depth=5, min_samples_leaf=5, class_weight="balanced", random_state=42
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=200, min_samples_leaf=3, class_weight="balanced", random_state=42
    ),
    "Logistic Regression": LogisticRegression(class_weight="balanced", max_iter=1000),
}

# 6. Use identical folds for every model
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scoring = {
    "accuracy": "accuracy",
    "pass_recall": make_scorer(recall_score, pos_label="Pass", zero_division=0),
    "pass_precision": make_scorer(precision_score, pos_label="Pass", zero_division=0),
    "pass_f1": make_scorer(f1_score, pos_label="Pass", zero_division=0),
}

# 7. Evaluate every model
for name, classifier in models.items():
    pipeline = Pipeline(
        steps=[("preprocessor", preprocessor), ("classifier", classifier)]
    )

    results = cross_validate(pipeline, X, y, cv=cv, scoring=scoring)

    print("\n" + "=" * 45)
    print(name)
    print("=" * 45)

    for metric in scoring:
        scores = results[f"test_{metric}"]
        print(f"{metric}: {scores.mean():.3f} +/- {scores.std():.3f}")
