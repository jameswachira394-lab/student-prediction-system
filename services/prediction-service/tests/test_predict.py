import os

import pytest
from fastapi.testclient import TestClient

# Configure environment for mock mode
os.environ["USE_MOCK_MODEL"] = "true"
os.environ["MODEL_PATH"] = "unused-in-mock-mode"

from app.main import app
from app.predict import Predictor


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_with_mock_model(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True


def test_predict_returns_agreed_shape(client):
    response = client.post(
        "/predict",
        json={"study_hours": 12, "attendance": 85, "previous_score": 64},
    )
    assert response.status_code == 200
    data = response.json()
    assert "predicted_score" in data
    assert 0 <= data["predicted_score"] <= 100
    assert data["risk"] in ("low", "medium", "high")
    assert "grade" in data
    assert data["model_version"] == "mock"
    assert "feature_importance" in data


def test_predict_missing_field(client):
    response = client.post(
        "/predict",
        json={"study_hours": 12, "attendance": 85},  # previous_score missing
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "request_id" in data


def test_predict_out_of_range(client):
    response = client.post(
        "/predict",
        json={
            "study_hours": 100,
            "attendance": 85,
            "previous_score": 64,
        },  # study_hours > 80
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_model_info(client):
    response = client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_version"] == "mock"
    assert len(data["fields"]) == 3
    assert "risk_thresholds" in data


def test_health_when_model_failed():
    # Test model_unavailable / failed state
    unloaded_app = TestClient(app)
    unloaded_app.app.state.predictor = None

    response = unloaded_app.get("/health")
    assert response.status_code == 503
    assert response.json()["model_loaded"] is False

    pred_res = unloaded_app.post(
        "/predict",
        json={"study_hours": 12, "attendance": 85, "previous_score": 64},
    )
    assert pred_res.status_code == 503
    assert pred_res.json()["error"]["code"] == "MODEL_UNAVAILABLE"


def test_predictor_missing_model_file():
    with pytest.raises(FileNotFoundError):
        Predictor.load(model_path="non_existent_file.joblib", use_mock=False)
