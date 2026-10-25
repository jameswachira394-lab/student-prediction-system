import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

# Placeholder values used only in mock mode. AI/ML sets the real ones in the model metadata.
MOCK_METADATA = {
    "version": "mock",
    "task": "regression",
    "fields": [
        {
            "name": "study_hours",
            "label": "Study hours per week",
            "unit": "hours",
            "min": 0,
            "max": 80,
            "hint": "Time you spend studying outside class each week.",
        },
        {
            "name": "attendance",
            "label": "Attendance",
            "unit": "%",
            "min": 0,
            "max": 100,
            "hint": "Share of classes you attended this term.",
        },
        {
            "name": "previous_score",
            "label": "Previous score",
            "unit": "%",
            "min": 0,
            "max": 100,
            "hint": "Your most recent exam or test result.",
        },
    ],
    "risk_thresholds": {"low": 65, "medium": 50},
    "grade_bands": [
        {"grade": "A", "min": 80},
        {"grade": "B", "min": 65},
        {"grade": "C", "min": 50},
        {"grade": "D", "min": 0},
    ],
    "metrics": {},
}


class Predictor:
    def __init__(self, metadata: dict[str, Any], pipeline: Any = None):
        self.metadata = metadata
        self.pipeline = pipeline  # None means mock mode
        self.field_names = [f["name"] for f in metadata.get("fields", [])]

    @classmethod
    def load(cls, model_path: str, use_mock: bool = False) -> Predictor:
        if use_mock:
            return cls(MOCK_METADATA)

        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(f"Model file not found at {model_path}")

        meta_path = path.with_suffix(".json")
        if not meta_path.exists():
            raise FileNotFoundError(f"Metadata file not found at {meta_path}")

        metadata = json.loads(meta_path.read_text())
        model = joblib.load(path)
        return cls(metadata, model)

    def predict(self, values: dict[str, Any]) -> dict[str, Any]:
        missing = [name for name in self.field_names if name not in values]
        if missing:
            raise ValueError(f"Missing values: {', '.join(missing)}.")

        # Safety-net range check
        for field in self.metadata.get("fields", []):
            name = field["name"]
            val = values[name]
            if not isinstance(val, (int, float)):
                raise TypeError(f"{field.get('label', name)} must be a number.")
            if not (field["min"] <= val <= field["max"]):
                raise ValueError(
                    f"{field.get('label', name)} must be between {field['min']} and {field['max']}."
                )

        if self.pipeline is None:
            # Mock formula from backend.md
            score = (
                0.5 * values["previous_score"]
                + 0.3 * values["attendance"]
                + 0.4 * values["study_hours"]
            )
        else:
            row = pd.DataFrame([{name: values[name] for name in self.field_names}])
            score = float(self.pipeline.predict(row)[0])

        score = round(max(0.0, min(100.0, score)), 1)
        thresholds = self.metadata["risk_thresholds"]
        if score >= thresholds["low"]:
            risk = "low"
        elif score >= thresholds["medium"]:
            risk = "medium"
        else:
            risk = "high"

        grade = next(
            b["grade"] for b in self.metadata["grade_bands"] if score >= b["min"]
        )

        return {
            "predicted_score": score,
            "grade": grade,
            "risk": risk,
            "model_version": self.metadata.get("version", "v1"),
            "feature_importance": {
                "attendance": 0.46,
                "study_hours": 0.33,
                "previous_score": 0.21,
            },
        }

    def info(self) -> dict[str, Any]:
        return {
            "model_version": self.metadata.get("version", "v1"),
            "task": self.metadata.get("task", "regression"),
            "fields": self.metadata.get("fields", []),
            "risk_thresholds": self.metadata.get("risk_thresholds", {}),
            "metrics": self.metadata.get("metrics", {}),
        }
