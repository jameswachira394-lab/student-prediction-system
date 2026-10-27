
import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import joblib

# 1. Load the cleaned dataset
df = pd.read_csv("data/processed/cleaned_dataset.csv")

# 2. Define the target and features
TARGET_COLUMN = "Pass_status"

X = df.drop(
    columns=[TARGET_COLUMN, "Student_ID", "Final_Exam_Score"]
)
y = df[TARGET_COLUMN]

# 3. Check the features
print("Features used by the model:")
print(X.columns.tolist())

# 4. Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTraining features:", X_train.shape)
print("Testing features:", X_test.shape)
print("Training target:", y_train.shape)
print("Testing target:", y_test.shape)

# 5. Identify categorical and numerical columns
categorical_columns = X_train.select_dtypes(
    include=["str", "object", "category", "bool"]
).columns.tolist()

numerical_columns = X_train.select_dtypes(
    include=["number"]
).columns.tolist()

# 6. Preprocess the data
preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_columns
        ),
        ("numerical", "passthrough", numerical_columns)
    ]
)

# 7. Create the classification pipeline
model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", DecisionTreeClassifier(random_state=42))
])

# 8. FIT: train the model
model.fit(X_train, y_train)
print("\nModel trained successfully.")

# 9. Evaluate the model on unseen test data
y_pred = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification report:")
print(classification_report(y_test, y_pred, zero_division=0))

# 10. Save the trained model
Path("models").mkdir(exist_ok=True)
joblib.dump(model, "models/pass_status_model.pkl")

print("\nModel saved successfully.")
print("Saved to: models/pass_status_model.pkl")
