import json
import time
import uuid
from datetime import UTC, datetime

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def log_event(
    service: str, level: str, message: str, request_id: str = "unknown"
) -> None:
    entry = {
        "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "level": level.lower(),
        "service": service,
        "request_id": request_id,
        "message": message,
    }
    print(json.dumps(entry), flush=True)


def error_response(
    status: int,
    code: str,
    message: str,
    request_id: str,
    details: list | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or [],
            },
            "request_id": request_id,
        },
    )


def install_common_handlers(
    app: FastAPI, service_name: str = "prediction-service"
) -> None:
    @app.middleware("http")
    async def request_id_and_logging_middleware(request: Request, call_next):
        start_time = time.time()
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        duration_ms = int((time.time() - start_time) * 1000)
        log_event(
            service=service_name,
            level="info",
            message=f"{request.method} {request.url.path} {response.status_code} in {duration_ms} ms",
            request_id=request_id,
        )
        return response

    @app.exception_handler(RequestValidationError)
    async def on_validation_error(request: Request, exc: RequestValidationError):
        details = [
            {"field": str(e["loc"][-1]), "issue": e["msg"]} for e in exc.errors()
        ]
        request_id = getattr(request.state, "request_id", "unknown")
        return error_response(
            422,
            "VALIDATION_ERROR",
            "Some values are missing or not valid.",
            request_id,
            details,
        )

    @app.exception_handler(Exception)
    async def on_unexpected_error(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", "unknown")
        log_event(
            service=service_name,
            level="error",
            message=f"Unexpected error: {exc!s}",
            request_id=request_id,
        )
        return error_response(
            500,
            "INTERNAL_ERROR",
            "Something went wrong on our side.",
            request_id,
        )
