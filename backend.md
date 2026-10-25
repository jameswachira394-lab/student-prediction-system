Backend Documentation

This file describes the backend of the Student Results Prediction System: the two services behind the gateway, what each one does, the endpoints and data formats, and the rules everyone follows when writing backend code.

It builds on DOCUMENTATION.md (ownership, architecture, processes) and design.md (what the frontend needs). Where this file extends the API contract from DOCUMENTATION.md, the extension is marked (proposed) and needs the agreement of all three team members before it becomes final.

Contents
Overview
Ownership
Tech stack
Folder structure
Conventions shared by both services
Prediction service
Results service
Errors
Configuration
Logging and health checks
Testing
Docker and running locally
Security and privacy
Phase 2: storing history
Suggested build order
Open items
1. Overview

The backend is two small FastAPI services. Only the results service is reachable from the browser, through the gateway. The prediction service is internal.

/api/*POST /predictGET /model-infophase 2BrowserGatewayResults serviceport 8000Prediction serviceport 8001Model filemodel_v1.joblibPostgres
Service	Job in one sentence
Results service	The public API: checks the input, asks the prediction service for a result, and returns it to the frontend
Prediction service	Loads the trained model once and turns a set of inputs into a score, a grade and a risk level

Request flow for one prediction:

The frontend sends POST /api/predictions through the gateway, which adds an X-Request-ID.
The results service checks that the values are numbers inside the allowed ranges.
It calls POST /predict on the prediction service, passing the same request ID.
The prediction service runs the model and returns the result.
The results service returns the result to the frontend. (Phase 2: it also saves it.)
2. Ownership
Area	Owner	Support
Model, predict.py, grade bands, risk thresholds, model metadata	AI/ML	DevOps
Prediction service API wrapper (main.py), Dockerfile, health check	DevOps	AI/ML
Results service (all of it)	DevOps	AI/ML
API contract (this file and DOCUMENTATION.md section 5)	DevOps	AI/ML, Frontend
Backend tests	Whoever writes the code	Reviewer checks them

The line between the two owners of the prediction service is Predictor (section 6.3). AI/ML writes and tests everything behind it. DevOps writes everything around it.

3. Tech stack
Part	Choice (proposed)	Why
Language	Python 3.11	Same as the ML work, one language for the whole backend
Web framework	FastAPI with Uvicorn	Automatic /docs page, clear request checking, easy to learn
Data checking	Pydantic	Comes with FastAPI
HTTP client (results to prediction)	httpx	Works with FastAPI's async style
Model	scikit-learn, joblib, pandas, numpy	Saved with joblib, loaded once at startup
Tests	pytest, FastAPI TestClient	Simple and fast
Lint and format	ruff	Same tool CI already runs
Phase 2 database	PostgreSQL, SQLAlchemy, Alembic	Only for storing history

Pin exact versions in each requirements.txt. The scikit-learn version must match the one the model was trained with (see section 6.5).

4. Folder structure
text
services/
├── prediction-service/
│   ├── app/
│   │   ├── main.py          # endpoints, startup (DevOps)
│   │   ├── errors.py        # shared error helpers (copy in both services)
│   │   └── predict.py       # Predictor class (AI/ML)
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
└── results-service/
    ├── app/
    │   ├── main.py          # endpoints, startup
    │   ├── errors.py        # same file as in the prediction service
    │   ├── validation.py    # range checks
    │   └── clients.py       # calls to the prediction service
    ├── tests/
    ├── requirements.txt
    └── Dockerfile
ml/
└── models/
    ├── model_v1.joblib
    └── model_v1.json        # metadata (section 6.5)

Two services keep their own copy of errors.py on purpose, so each service can be built and released alone. The contract tests in section 11 catch the copies drifting apart.

5. Conventions shared by both services
Format: JSON in and out. Field names are snake_case.
Request ID: every request has an X-Request-ID. If the header is missing, the service creates one. The ID is returned in the response header, included in error bodies, written in every log line, and passed on to any service called.
Status codes: 200 success, 422 input is not valid, 503 a needed service or the model is unavailable, 500 unexpected error. Use 404 for unknown paths.
Errors: always the one shared shape in section 8. Never return a stack trace.
Health: every service has a GET /health (the results service's is GET /api/health, because the gateway sends all /api traffic to it).
No hidden state: both services work the same way after a restart. The model is read from disk at startup and nothing else is stored in phase 1.
Numbers: scores are rounded to one decimal place. Percentages are numbers from 0 to 100, not fractions.
Paths: the results service defines its routes with the /api prefix included, and the gateway forwards /api/... without changing it.
6. Prediction service

Internal only. Port 8001. Never called by the browser.

6.1 Endpoints
Method and path	Purpose
POST /predict	Return a prediction for one set of inputs
GET /model-info	Describe the model: version, input fields with ranges, risk thresholds, metrics
GET /health	Say whether the service is up and the model is loaded
6.2 POST /predict

Request:

json
{ "study_hours": 12, "attendance": 85, "previous_score": 64 }

Response 200:

json
{
  "predicted_score": 72.4,
  "grade": "B",
  "risk": "low",
  "model_version": "v1",
  "feature_importance": {
    "attendance": 0.46,
    "study_hours": 0.33,
    "previous_score": 0.21
  }
}
Field	Type	Meaning
predicted_score	number	Predicted result, 0 to 100, one decimal place
grade	string	Letter grade from the grade bands in the model metadata
risk	string	low, medium or high, from the risk thresholds in the model metadata
model_version	string	For example v1, or mock in mock mode
feature_importance	object	(proposed, optional) Share of the estimate each input accounts for. The values add up to 1. If the model cannot provide it, leave the field out. The frontend then hides the influence card

Errors: 422 VALIDATION_ERROR for missing, non-numeric or out-of-range values, 503 MODEL_UNAVAILABLE if the model did not load.

6.3 The Predictor class (the AI/ML boundary)

app/predict.py holds one class that the API wrapper uses. The wrapper never touches scikit-learn directly. This is what AI/ML must provide:

Member	Contract
Predictor.load(model_path, use_mock)	Reads the model file and its metadata once. With use_mock=True it needs no files
predict(values: dict) -> dict	Takes the input fields by name, returns predicted_score, grade, risk, model_version and optionally feature_importance. Raises ValueError with a readable message for bad input
info() -> dict	Returns the model description used by GET /model-info (section 6.4)

Rules for predict:

It does no file or network work. The model is already in memory.
The same input always gives the same output.
It uses a pandas DataFrame with the same column names the model was trained with, so a Pipeline with preprocessing works unchanged.
The score is clamped to 0 to 100.
It is covered by unit tests (section 11).

A reference skeleton, to be replaced by the real implementation:

python
import json
from pathlib import Path

import joblib
import pandas as pd

# Placeholder values used only in mock mode. AI/ML sets the real ones in the model metadata.
MOCK_METADATA = {
    "version": "mock",
    "task": "regression",
    "fields": [
        {"name": "study_hours", "label": "Study hours per week", "unit": "hours", "min": 0, "max": 80},
        {"name": "attendance", "label": "Attendance", "unit": "%", "min": 0, "max": 100},
        {"name": "previous_score", "label": "Previous score", "unit": "%", "min": 0, "max": 100},
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
    def __init__(self, metadata: dict, pipeline=None):
        self.metadata = metadata
        self.pipeline = pipeline  # None means mock mode
        self.field_names = [f["name"] for f in metadata["fields"]]

    @classmethod
    def load(cls, model_path: str, use_mock: bool = False) -> "Predictor":
        if use_mock:
            return cls(MOCK_METADATA)
        path = Path(model_path)
        metadata = json.loads(path.with_suffix(".json").read_text())
        return cls(metadata, joblib.load(path))

    def predict(self, values: dict) -> dict:
        missing = [name for name in self.field_names if name not in values]
        if missing:
            raise ValueError(f"Missing values: {', '.join(missing)}.")
        if self.pipeline is None:
            score = 0.5 * values["previous_score"] + 0.3 * values["attendance"] + 0.4 * values["study_hours"]
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
        grade = next(b["grade"] for b in self.metadata["grade_bands"] if score >= b["min"])
        return {
            "predicted_score": score,
            "grade": grade,
            "risk": risk,
            "model_version": self.metadata["version"],
        }

    def info(self) -> dict:
        return {
            "model_version": self.metadata["version"],
            "task": self.metadata["task"],
            "fields": self.metadata["fields"],
            "risk_thresholds": self.metadata["risk_thresholds"],
            "metrics": self.metadata.get("metrics", {}),
        }

Mock mode (USE_MOCK_MODEL=true) returns a simple made-up formula with exactly the same response shape. It exists so the frontend, the results service and CI can all work before the real model is ready. Mock results must never be shown as real predictions: the response says "model_version": "mock".

6.4 GET /model-info (proposed)

This endpoint lets the frontend build its form and draw the gauge without hard-coding ranges, and lets the results service check input against the same ranges.

json
{
  "model_version": "v1",
  "task": "regression",
  "fields": [
    { "name": "study_hours", "label": "Study hours per week", "unit": "hours", "min": 0, "max": 80, "hint": "Time you spend studying outside class each week." },
    { "name": "attendance", "label": "Attendance", "unit": "%", "min": 0, "max": 100, "hint": "Share of classes you attended this term." },
    { "name": "previous_score", "label": "Previous score", "unit": "%", "min": 0, "max": 100, "hint": "Your most recent exam or test result." }
  ],
  "risk_thresholds": { "low": 65, "medium": 50 },
  "metrics": { "mae": 6.1, "baseline_mae": 11.4 }
}

The numbers are placeholders until AI/ML finishes the model. hint is optional.

How risk_thresholds is read: a score at or above low is low risk, at or above medium is medium risk, and anything below is high risk. The frontend uses the same two numbers to draw the gauge zones.

6.5 Model files and metadata

Each model version is a pair of files in ml/models/:

model_v1.joblib: the trained scikit-learn Pipeline (preprocessing and model together).
model_v1.json: the metadata the service reads.

The metadata in DOCUMENTATION.md section 6.4 lists features as plain names. This file proposes replacing it with a fields list so GET /model-info can be built straight from the file. Update that example when the team agrees.

json
{
  "version": "v1",
  "trained_on": "2026-10-20",
  "python_version": "3.11",
  "scikit_learn_version": "1.5.2",
  "task": "regression",
  "fields": [
    { "name": "study_hours", "label": "Study hours per week", "unit": "hours", "min": 0, "max": 80 },
    { "name": "attendance", "label": "Attendance", "unit": "%", "min": 0, "max": 100 },
    { "name": "previous_score", "label": "Previous score", "unit": "%", "min": 0, "max": 100 }
  ],
  "risk_thresholds": { "low": 65, "medium": 50 },
  "grade_bands": [
    { "grade": "A", "min": 80 },
    { "grade": "B", "min": 65 },
    { "grade": "C", "min": 50 },
    { "grade": "D", "min": 0 }
  ],
  "metrics": { "mae": 6.1, "baseline_mae": 11.4 },
  "notes": "Trained on <dataset name>. Not validated for other schools."
}

All numbers, grade letters and field ranges here are placeholders. AI/ML decides the real grade bands, thresholds and ranges and records them here. The ranges should come from what the training data actually covers.

Loading rules:

The service reads MODEL_PATH once at startup.
If loading fails, the service stays up but GET /health returns 503 and /predict returns 503 MODEL_UNAVAILABLE. The failure is logged with its reason.
The python_version and scikit_learn_version in the metadata must match the service. CI loads the model and makes one prediction to catch a mismatch.
6.6 API wrapper skeleton (main.py)

Plain def endpoints are used on purpose. FastAPI runs them in a worker thread, so a slow model call does not block other requests.

python
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.errors import error_response, install_common_handlers
from app.predict import Predictor

logger = logging.getLogger("prediction-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.predictor = None
    try:
        app.state.predictor = Predictor.load(
            model_path=os.environ["MODEL_PATH"],
            use_mock=os.getenv("USE_MOCK_MODEL", "false").lower() == "true",
        )
    except Exception:
        logger.exception("The model failed to load")
    yield


app = FastAPI(title="Prediction service", lifespan=lifespan)
install_common_handlers(app)


class PredictRequest(BaseModel):
    study_hours: float
    attendance: float
    previous_score: float


def model_unavailable(request: Request) -> JSONResponse:
    return error_response(503, "MODEL_UNAVAILABLE", "The model is not loaded.", request.state.request_id)


@app.get("/health")
def health(request: Request):
    loaded = request.app.state.predictor is not None
    body = {"status": "ok" if loaded else "unavailable", "model_loaded": loaded}
    return JSONResponse(body, status_code=200 if loaded else 503)


@app.get("/model-info")
def model_info(request: Request):
    predictor = request.app.state.predictor
    if predictor is None:
        return model_unavailable(request)
    return predictor.info()


@app.post("/predict")
def predict(body: PredictRequest, request: Request):
    predictor = request.app.state.predictor
    if predictor is None:
        return model_unavailable(request)
    try:
        return predictor.predict(body.model_dump())
    except ValueError as problem:
        return error_response(422, "VALIDATION_ERROR", str(problem), request.state.request_id)

The service also checks ranges as a safety net. Add the same check_ranges function used in the results service (section 7.4) inside Predictor.predict, so a direct call to the prediction service cannot return a score for nonsense input.

7. Results service

The public API. Port 8000. The gateway sends every /api/... request here.

7.1 Endpoints
Method and path	Purpose	Phase
POST /api/predictions	Check the input, get a prediction, return it (phase 2: also store it)	1
GET /api/model-info	Pass the model description through to the frontend	1
GET /api/health	Health of this service and the prediction service	1
GET /api/predictions?limit=20	Recent predictions	2
GET /api/summary	Counts by risk level, for a teacher view	2
7.2 POST /api/predictions

Request, the same fields as the prediction service:

json
{ "study_hours": 12, "attendance": 85, "previous_score": 64 }

Response 200, the prediction service's response unchanged:

json
{
  "predicted_score": 72.4,
  "grade": "B",
  "risk": "low",
  "model_version": "v1",
  "feature_importance": { "attendance": 0.46, "study_hours": 0.33, "previous_score": 0.21 }
}

In phase 2 the response also carries id and created_at of the stored record.

Case	Status	Error code
Success	200	none
A field is missing, is not a number, or is outside its range	422	VALIDATION_ERROR
The prediction service cannot be reached, times out, or answers with an error	503	MODEL_UNAVAILABLE
Anything unexpected in this service	500	INTERNAL_ERROR
7.3 GET /api/model-info

Returns the prediction service's GET /model-info response as is. The results service may keep it in memory for a few minutes, because it only changes when a new model is released. If the prediction service cannot be reached, it returns 503 MODEL_UNAVAILABLE.

7.4 Range checks

The ranges live in one place: the model metadata. The results service reads them from GET /model-info and checks every request against them, so a new model with new ranges needs no change here.

python
def check_ranges(values: dict, fields: list[dict]) -> list[dict]:
    """Return one problem per value that is outside its allowed range."""
    problems = []
    for field in fields:
        value = values[field["name"]]
        if not field["min"] <= value <= field["max"]:
            problems.append(
                {"field": field["name"], "issue": f"must be between {field['min']} and {field['max']}"}
            )
    return problems

The error message shown to the student is built as the field label plus the issue, for example "Attendance must be between 0 and 100." The frontend design uses exactly this wording. Missing or non-numeric values are caught earlier by Pydantic and reported through the same error shape.

7.5 Endpoint skeleton (main.py)
python
import os

import httpx
from fastapi import FastAPI, Request
from pydantic import BaseModel

from app.errors import error_response, install_common_handlers
from app.validation import check_ranges

PREDICTION_SERVICE_URL = os.environ["PREDICTION_SERVICE_URL"]
TIMEOUT_SECONDS = float(os.getenv("PREDICTION_TIMEOUT_SECONDS", "5"))

app = FastAPI(title="Results service")
install_common_handlers(app)


class PredictionRequest(BaseModel):
    study_hours: float
    attendance: float
    previous_score: float


@app.post("/api/predictions")
async def create_prediction(body: PredictionRequest, request: Request):
    request_id = request.state.request_id
    headers = {"X-Request-ID": request_id}
    values = body.model_dump()
    try:
        # In real code, create one client at startup and cache model-info for a few minutes.
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            info = (await client.get(f"{PREDICTION_SERVICE_URL}/model-info", headers=headers)).json()
            problems = check_ranges(values, info["fields"])
            if problems:
                first = problems[0]
                label = next(f["label"] for f in info["fields"] if f["name"] == first["field"])
                return error_response(422, "VALIDATION_ERROR", f"{label} {first['issue']}.", request_id, problems)
            response = await client.post(f"{PREDICTION_SERVICE_URL}/predict", json=values, headers=headers)
            response.raise_for_status()
    except (httpx.RequestError, httpx.HTTPStatusError, KeyError, ValueError):
        return error_response(503, "MODEL_UNAVAILABLE", "The prediction service is not answering.", request_id)
    return response.json()

Calling the prediction service:

Total timeout 5 seconds, set by PREDICTION_TIMEOUT_SECONDS (proposed).
A prediction is read-only, so one retry after a connection error is safe. Do not retry after a timeout or an error response.
Always pass X-Request-ID on.
7.6 GET /api/health
json
{ "status": "ok", "dependencies": { "prediction_service": "ok" } }

The results service calls the prediction service's GET /health. If that fails, it returns 503 with "status": "degraded" and "prediction_service": "unavailable". The public uptime check and the CI smoke test both use this endpoint.

One consequence to know about: if the prediction service goes down, Docker will also mark the results service unhealthy. That is acceptable for version 1. If it becomes a problem, add a separate GET /api/health/live that checks only the results service itself, and point the Docker health check at that.

8. Errors

Both services return every error in this shape:

json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Attendance must be between 0 and 100.",
    "details": [
      { "field": "attendance", "issue": "must be between 0 and 100" }
    ]
  },
  "request_id": "b6f1c2a0-0000-0000-0000-000000000000"
}
Code	Status	When	Message guidance
VALIDATION_ERROR	422	Input is missing, wrong type or out of range	Say what is wrong and what is allowed, in plain words
MODEL_UNAVAILABLE	503	The model did not load, or the prediction service did not answer	Say it is temporary
NOT_FOUND	404	Unknown path or record	Short and neutral
INTERNAL_ERROR	500	Unexpected failure	Say something went wrong on our side. Never include the exception text

Messages are written for students, not developers. The real cause goes to the logs, not to the browser.

app/errors.py, the same file in both services:

python
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def error_response(status: int, code: str, message: str, request_id: str, details: list | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "error": {"code": code, "message": message, "details": details or []},
            "request_id": request_id,
        },
    )


def install_common_handlers(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.exception_handler(RequestValidationError)
    async def on_validation_error(request: Request, exc: RequestValidationError):
        details = [{"field": str(e["loc"][-1]), "issue": e["msg"]} for e in exc.errors()]
        request_id = getattr(request.state, "request_id", "unknown")
        return error_response(422, "VALIDATION_ERROR", "Some values are missing or not valid.", request_id, details)

    @app.exception_handler(Exception)
    async def on_unexpected_error(request: Request, exc: Exception):
        # The real error is logged by the server. The client only gets a safe message.
        request_id = getattr(request.state, "request_id", "unknown")
        return error_response(500, "INTERNAL_ERROR", "Something went wrong on our side.", request_id)
9. Configuration

All settings are environment variables. .env.example lists every one with a safe placeholder, and .env is never committed.

Variable	Service	Example	Purpose
MODEL_PATH	prediction	/app/models/model_v1.joblib	Model file. The metadata is read from the same path with .json
USE_MOCK_MODEL	prediction	false	true returns fake predictions with the real response shape
LOG_LEVEL	both	info	Logging detail
PREDICTION_SERVICE_URL	results	http://prediction-service:8001	Where to reach the model service
PREDICTION_TIMEOUT_SECONDS	results	5	Total time allowed for a call to the prediction service (proposed)
CORS_ALLOWED_ORIGINS	results	http://localhost:5173	Local development only. Leave empty when running behind the gateway
DATABASE_URL	results	postgresql://user:pass@postgres:5432/results	Phase 2 only. Contains a secret

Read settings once at startup. A required setting that is missing should stop the service with a clear message instead of failing later.

10. Logging and health checks

Logging

One JSON object per line to standard output, so docker compose logs works everywhere.
Required fields: timestamp, level, service, request_id, message.
For each request also log the method, path, status code and how long it took.
Do not log the submitted values or any secret. The request ID is enough to follow one request across both services.
json
{"timestamp": "2026-10-25T08:30:12Z", "level": "info", "service": "results-service", "request_id": "b6f1c2a0-0000-0000-0000-000000000000", "message": "POST /api/predictions 200 in 41 ms"}

Health checks

Service	Endpoint	Healthy when
Prediction service	GET /health	The model is loaded. Otherwise 503
Results service	GET /api/health	It is running and can reach the prediction service. Otherwise 503

Docker uses these in HEALTHCHECK. Compose starts the results service only after the prediction service is healthy.

11. Testing

Tests run in CI for each service (pytest). Every endpoint needs at least one success test and one failure test.

Prediction service

Test	Checks
Health with the mock model	200 and model_loaded is true
Health when the model is missing	503
Predict with valid input	Response has predicted_score, grade, risk, model_version
Predict with a missing field	422 in the shared error shape
Output ranges	Score is between 0 and 100, risk is one of the three values
Model files (once the real model exists)	model_v1.joblib loads and makes one prediction. This is the check that catches a scikit-learn version mismatch
Risk and grade mapping	Scores on each side of each threshold and band give the expected risk and grade

Results service

Test	Checks
Valid request, prediction service answers	200 and the body is passed through
Out-of-range value	422, VALIDATION_ERROR, and the message "Attendance must be between 0 and 100."
Missing field or text instead of a number	422 in the shared error shape
Prediction service down or too slow	503, MODEL_UNAVAILABLE
Health with the prediction service up and down	200 and 503
Request ID	Sent in, it comes back in the header and in error bodies. Missing, it is created

Fake the prediction service in these tests with a small stand-in (for example the respx package, which fakes httpx calls), so they do not need Docker.

A first test, to show the pattern (the mock model is switched on before the app loads):

python
import os

os.environ["USE_MOCK_MODEL"] = "true"
os.environ["MODEL_PATH"] = "unused-in-mock-mode"

from fastapi.testclient import TestClient

from app.main import app


def test_predict_returns_the_agreed_shape():
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            json={"study_hours": 12, "attendance": 85, "previous_score": 64},
        )
    body = response.json()
    assert response.status_code == 200
    assert 0 <= body["predicted_score"] <= 100
    assert body["risk"] in ("low", "medium", "high")
    assert {"grade", "model_version"} <= body.keys()

Contract checks (proposed). Keep one example request and one example response as JSON files in a contracts/ folder at the repository root. Both services test against them, and the frontend can use the same files as its mock data. If someone changes a field in one place, a test fails in the other.

CI smoke test. CI starts the whole stack and calls /api/health and /api/predictions through the gateway (see DOCUMENTATION.md section 6.6).

12. Docker and running locally

Follow the Docker standards in DOCUMENTATION.md section 7.3: pinned base image, non-root user, .dockerignore, one process per container, a health check, no secrets in the image.

Prediction service. It needs the model from ml/models/, which sits outside its own folder, so it is built from the repository root. CI already builds it this way.

dockerfile
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY services/prediction-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/prediction-service/app ./app
COPY ml/models ./models
RUN useradd --create-home appuser
USER appuser
EXPOSE 8001
HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

Results service. It is built from its own folder. Its Dockerfile is the same pattern with port 8000, no model copy, and a health check on http://localhost:8000/api/health.

Compose. Because the prediction service builds from the root, its entry in docker-compose.yml needs a context and a Dockerfile path. This replaces the build: ./services/prediction-service line in the compose skeleton in DOCUMENTATION.md section 3.6:

yaml
  prediction-service:
    build:
      context: .
      dockerfile: services/prediction-service/Dockerfile
    environment:
      MODEL_PATH: /app/models/model_v1.joblib
      USE_MOCK_MODEL: ${USE_MOCK_MODEL:-false}

Run one service without Docker (useful while developing):

bash
cd services/prediction-service
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
USE_MOCK_MODEL=true MODEL_PATH=unused uvicorn app.main:app --reload --port 8001

Then open http://localhost:8001/docs to try the endpoints from the browser. The results service works the same way on port 8000, with PREDICTION_SERVICE_URL=http://localhost:8001.

13. Security and privacy
The prediction service and the database are never exposed outside the Docker network. Only the gateway is public.
Check all input on the server, even though the frontend checks it too.
Never return stack traces or internal addresses in error messages.
Keep secrets in environment variables and the CI secret store, never in code or images.
Set a request size limit and rate limiting at the gateway to protect the prediction service (proposed).
CORS stays off behind the gateway because the browser and API share one origin. Turn it on only for local development.
Do not log submitted values. Do not collect names, emails or student numbers. Do not use gender, ethnicity or other sensitive attributes as model inputs.
Update dependencies regularly. Dependabot opens the pull requests, and scikit-learn upgrades are done on purpose together with AI/ML, followed by retraining.
14. Phase 2: storing history

Only if the team decides to add history and a teacher view. The results service gets a Postgres database, and only the results service talks to it.

sql
CREATE TABLE predictions (
    id              UUID PRIMARY KEY,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    study_hours     NUMERIC(5, 2) NOT NULL,
    attendance      NUMERIC(5, 2) NOT NULL,
    previous_score  NUMERIC(5, 2) NOT NULL,
    predicted_score NUMERIC(5, 2) NOT NULL,
    grade           TEXT NOT NULL,
    risk            TEXT NOT NULL CHECK (risk IN ('low', 'medium', 'high')),
    model_version   TEXT NOT NULL
);

CREATE INDEX predictions_created_at_idx ON predictions (created_at DESC);
The table has no name, email or student number on purpose. If the team later needs "one student's history", decide first how students are identified, and what the privacy rules are.
Schema changes go through Alembic migrations that run when the results service starts or in a separate step. Never edit tables by hand.
POST /api/predictions saves the record after a successful prediction and adds id and created_at to the response. If saving fails, still return the prediction and log the problem, because the student's answer matters more than the history.
GET /api/predictions?limit=20 returns the newest records first, limit between 1 and 100.
GET /api/summary returns counts by risk level:
json
{ "total": 120, "by_risk": { "low": 70, "medium": 35, "high": 15 } }

The numbers above are an example of the shape, not real data.

Back up the database volume before each deployment, and keep the database password in the secret store.
15. Suggested build order
Agree the contract. Review sections 6.2, 6.4 and 7.2 together and settle the proposed items.
Prediction service in mock mode. Write main.py, errors.py and the mock Predictor. Run it locally and check /docs.
Results service. Write POST /api/predictions, GET /api/model-info and GET /api/health against the mock. The frontend can now start.
Tests. Add the tests from section 11 and make sure CI runs them.
Dockerfiles and Compose. Build both images and start the stack with docker compose up.
Real model. AI/ML replaces the mock path in Predictor, adds model_v1.joblib and model_v1.json, and the model-load test goes in CI. Set USE_MOCK_MODEL=false.
Hardening. Logging, request IDs, timeouts and error messages checked against sections 5, 7 and 8.
Phase 2, if time allows. Database, history and summary endpoints.
16. Open items
Final input fields, units and ranges (AI/ML).
Grade bands and risk thresholds (AI/ML).
Whether feature_importance is in version 1 (AI/ML).
Agreement on GET /model-info, the extended metadata fields list and PREDICTION_TIMEOUT_SECONDS (all three).
Whether to add a separate liveness endpoint (DevOps).
Update DOCUMENTATION.md sections 3.6, 5 and 6.4 to match what is agreed here (DevOps).
Phase 2 decision: history, teacher view, and how students would be identified (whole team).