from unittest.mock import AsyncMock, patch

import pytest
from app.main import app, client
from fastapi.testclient import TestClient

MOCK_INFO = {
    "model_version": "mock",
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
    "metrics": {},
}

MOCK_PREDICTION = {
    "predicted_score": 72.4,
    "grade": "B",
    "risk": "low",
    "model_version": "mock",
    "feature_importance": {
        "attendance": 0.46,
        "study_hours": 0.33,
        "previous_score": 0.21,
    },
}


@pytest.fixture
def test_client():
    with TestClient(app) as test_c:
        yield test_c


def test_health_ok(test_client):
    with patch.object(client, "get_health", new_callable=AsyncMock) as mock_health:
        mock_health.return_value = (True, {"status": "ok", "model_loaded": True})
        response = test_client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["dependencies"]["prediction_service"] == "ok"


def test_health_degraded(test_client):
    with patch.object(client, "get_health", new_callable=AsyncMock) as mock_health:
        mock_health.return_value = (False, {"status": "unavailable"})
        response = test_client.get("/api/health")
        assert response.status_code == 503
        assert response.json()["status"] == "degraded"
        assert response.json()["dependencies"]["prediction_service"] == "unavailable"


def test_model_info_success(test_client):
    with patch.object(client, "get_model_info", new_callable=AsyncMock) as mock_info:
        mock_info.return_value = MOCK_INFO
        response = test_client.get("/api/model-info")
        assert response.status_code == 200
        assert response.json()["model_version"] == "mock"
        assert len(response.json()["fields"]) == 3


def test_model_info_failure(test_client):
    with patch.object(client, "get_model_info", new_callable=AsyncMock) as mock_info:
        mock_info.side_effect = RuntimeError("Service unavailable")
        response = test_client.get("/api/model-info")
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "MODEL_UNAVAILABLE"


def test_predict_success(test_client):
    with (
        patch.object(client, "get_model_info", new_callable=AsyncMock) as mock_info,
        patch.object(client, "predict", new_callable=AsyncMock) as mock_predict,
    ):
        mock_info.return_value = MOCK_INFO
        mock_predict.return_value = MOCK_PREDICTION

        response = test_client.post(
            "/api/predictions",
            json={"study_hours": 12, "attendance": 85, "previous_score": 64},
            headers={"X-Request-ID": "test-req-1234"},
        )
        assert response.status_code == 200
        assert response.headers.get("X-Request-ID") == "test-req-1234"
        assert response.json() == MOCK_PREDICTION


def test_predict_out_of_range_attendance(test_client):
    with patch.object(client, "get_model_info", new_callable=AsyncMock) as mock_info:
        mock_info.return_value = MOCK_INFO

        response = test_client.post(
            "/api/predictions",
            json={"study_hours": 12, "attendance": 105, "previous_score": 64},
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert data["error"]["message"] == "Attendance must be between 0 and 100."
        assert data["error"]["details"][0]["field"] == "attendance"


def test_predict_missing_field(test_client):
    response = test_client.post(
        "/api/predictions",
        json={"study_hours": 12, "attendance": 85},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_predict_service_down(test_client):
    with patch.object(client, "get_model_info", new_callable=AsyncMock) as mock_info:
        mock_info.side_effect = RuntimeError("Connection refused")
        response = test_client.post(
            "/api/predictions",
            json={"study_hours": 12, "attendance": 85, "previous_score": 64},
        )
        assert response.status_code == 503
        data = response.json()
        assert data["error"]["code"] == "MODEL_UNAVAILABLE"
