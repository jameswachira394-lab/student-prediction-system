import os
from contextlib import asynccontextmanager

from app.errors import error_response, install_common_handlers, log_event
from app.predict import Predictor
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.predictor = None
    use_mock = os.getenv("USE_MOCK_MODEL", "false").lower() == "true"
    model_path = os.getenv("MODEL_PATH", "/app/models/model_v1.joblib")
    try:
        app.state.predictor = Predictor.load(
            model_path=model_path,
            use_mock=use_mock,
        )
        log_event(
            service="prediction-service",
            level="info",
            message=f"Predictor loaded successfully (mock={use_mock})",
        )
    except Exception as exc:  # noqa: BLE001
        log_event(
            service="prediction-service",
            level="error",
            message=f"The model failed to load: {exc}",
        )
    yield


app = FastAPI(title="Prediction service", lifespan=lifespan)
install_common_handlers(app, "prediction-service")


class PredictRequest(BaseModel):
    study_hours: float
    attendance: float
    previous_score: float


def model_unavailable(request: Request) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    return error_response(
        503,
        "MODEL_UNAVAILABLE",
        "The model is not loaded.",
        request_id,
    )


@app.get("/health")
def health(request: Request):
    loaded = getattr(request.app.state, "predictor", None) is not None
    body = {"status": "ok" if loaded else "unavailable", "model_loaded": loaded}
    return JSONResponse(body, status_code=200 if loaded else 503)


@app.get("/model-info")
def model_info(request: Request):
    predictor = getattr(request.app.state, "predictor", None)
    if predictor is None:
        return model_unavailable(request)
    return predictor.info()


@app.post("/predict")
def predict(body: PredictRequest, request: Request):
    predictor = getattr(request.app.state, "predictor", None)
    request_id = getattr(request.state, "request_id", "unknown")
    if predictor is None:
        return model_unavailable(request)
    try:
        return predictor.predict(body.model_dump())
    except (ValueError, TypeError) as problem:
        return error_response(
            422,
            "VALIDATION_ERROR",
            str(problem),
            request_id,
        )
