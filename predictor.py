
from pathlib import Path

import joblib
import pandas as pd


# Locate the saved model relative to this file
PROJECT_DIR = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_DIR / "models" / "pass_status_model.pkl"

# These must match the features used during training
FEATURE_COLUMNS = [
    "Gender",
    "Study_Hours_per_Week",
    "Attendance_Rate",
    "Past_Exam_Scores",
    "Parental_Education_Level",
    "Internet_Access_at_Home",
    "Extracurricular_Activities",
]


def load_trained_model():
    """Load the saved machine-learning pipeline."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def predict_student(student_data, model=None):
    """
    Predict a student's Pass/Fail status.

    student_data must be a dictionary containing all
    seven required input features.
    """
    missing_features = [
        feature
        for feature in FEATURE_COLUMNS
        if feature not in student_data
    ]

    if missing_features:
        raise ValueError(
            f"Missing required features: {missing_features}"
        )

    # Keep only the expected features and preserve their order
    student = pd.DataFrame(
        [{feature: student_data[feature]
          for feature in FEATURE_COLUMNS}]
    )

    if model is None:
        model = load_trained_model()

    prediction = model.predict(student)[0]
    probabilities = model.predict_proba(student)[0]

    return {
        "predicted_status": str(prediction),
        "probabilities": {
            str(label): float(probability)
            for label, probability
            in zip(model.classes_, probabilities)
        },
    }
