import joblib
from pathlib import Path

model_path = Path("models/pass_status_model.pkl")

if model_path.exists():
    print("Model file exists.")
    model = joblib.load(model_path)
    print("Saved model loaded successfully.")
else:
    print("Model file not found.")
