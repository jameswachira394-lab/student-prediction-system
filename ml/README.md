# AI/ML Module

This directory contains the machine learning datasets, training pipelines, model evaluation experiments, and saved models for predicting student performance.

## Overview

- **Algorithm:** Logistic Regression (scikit-learn Pipeline)
- **Saved model:** `models/pass_status_model.pkl`
- **Prediction module:** `predictor.py`
- **Target variable:** `Pass_status`

## Input Features

The model uses seven features:
- `Gender`
- `Study_Hours_per_Week`
- `Attendance_Rate`
- `Past_Exam_Scores`
- `Parental_Education_Level`
- `Internet_Access_at_Home`
- `Extracurricular_Activities`

## Model Evaluation

On the current held-out test set:
- Accuracy: ~75%
- Pass precision: ~55%
- Pass recall: ~72%
- Pass F1-score: ~63%

## Directory Structure

```text
ml/
├── data/
│   └── processed/
│       └── cleaned_dataset.csv
├── models/
│   └── pass_status_model.pkl
├── tests/
│   ├── test_predictor.py
│   └── test_saved_model.py
├── clean_data.py
├── compare_cross_validation.py
├── compare_models.py
├── compare_tuned_models.py
├── cross_validate_model.py
├── evaluate_model.py
├── inspect_data.py
├── predict_student.py
├── predictor.py
├── rename_columns.py
├── train_best_model.py
├── train_model.py
├── train.py -> train_best_model.py
├── tune_model.py
├── requirements.txt
└── README.md
```

## Running the Prediction Module

Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the unit tests:

```bash
python -m unittest discover tests/ -v
```

Run a sample prediction:

```bash
python predict_student.py
```

## Limitations

Predictions and probabilities are estimates based on historical student data, not guarantees. The model should be used as supportive guidance rather than the sole basis for academic decisions.
