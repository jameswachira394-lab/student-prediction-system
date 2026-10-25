import os

from app.clients import PredictionServiceClient
from app.errors import error_response, install_common_handlers
from app.validation import check_ranges
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

PREDICTION_SERVICE_URL = os.environ.get(
    "PREDICTION_SERVICE_URL", "http://prediction-service:8001"
)
TIMEOUT_SECONDS = float(os.getenv("PREDICTION_TIMEOUT_SECONDS", "5"))
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

client = PredictionServiceClient(
    base_url=PREDICTION_SERVICE_URL, timeout=TIMEOUT_SECONDS
)

app = FastAPI(title="Results service")

if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

install_common_handlers(app, "results-service")


class PredictionRequest(BaseModel):
    study_hours: float
    attendance: float
    previous_score: float


@app.get("/api/health")
async def health(request: Request):
    request_id = getattr(request.state, "request_id", "unknown")
    is_healthy, _ = await client.get_health(request_id=request_id)
    if is_healthy:
        return JSONResponse(
            {"status": "ok", "dependencies": {"prediction_service": "ok"}},
            status_code=200,
        )
    return JSONResponse(
        {
            "status": "degraded",
            "dependencies": {"prediction_service": "unavailable"},
        },
        status_code=503,
    )


@app.get("/api/model-info")
async def model_info(request: Request):
    request_id = getattr(request.state, "request_id", "unknown")
    try:
        return await client.get_model_info(request_id=request_id)
    except Exception:  # noqa: BLE001
        return error_response(
            503,
            "MODEL_UNAVAILABLE",
            "The prediction service is not answering.",
            request_id,
        )


@app.post("/api/predictions")
async def create_prediction(body: PredictionRequest, request: Request):
    request_id = getattr(request.state, "request_id", "unknown")
    values = body.model_dump()

    try:
        info = await client.get_model_info(request_id=request_id)
    except Exception:  # noqa: BLE001
        return error_response(
            503,
            "MODEL_UNAVAILABLE",
            "The prediction service is not answering.",
            request_id,
        )

    fields = info.get("fields", [])
    problems = check_ranges(values, fields)
    if problems:
        first = problems[0]
        label = next(
            (f["label"] for f in fields if f["name"] == first["field"]),
            first["field"].replace("_", " ").capitalize(),
        )
        return error_response(
            422,
            "VALIDATION_ERROR",
            f"{label} {first['issue']}.",
            request_id,
            problems,
        )

    try:
        return await client.predict(values, request_id=request_id)
    except Exception:  # noqa: BLE001
        return error_response(
            503,
            "MODEL_UNAVAILABLE",
            "The prediction service is not answering.",
            request_id,
        )
