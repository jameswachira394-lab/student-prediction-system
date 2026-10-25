import os
import time
from typing import Any

import httpx


class PredictionServiceClient:
    def __init__(self, base_url: str | None = None, timeout: float = 5.0):
        self.base_url = (
            base_url
            or os.environ.get(
                "PREDICTION_SERVICE_URL", "http://prediction-service:8001"
            )
        ).rstrip("/")
        self.timeout = timeout
        self._cached_info: dict[str, Any] | None = None
        self._cached_time: float = 0
        self._cache_ttl: float = 300.0  # 5 minutes cache

    async def get_health(self, request_id: str = "unknown") -> tuple[bool, dict]:
        headers = {"X-Request-ID": request_id}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(f"{self.base_url}/health", headers=headers)
                return res.status_code == 200, res.json()
        except Exception:  # noqa: BLE001
            return False, {"status": "unavailable"}

    async def get_model_info(self, request_id: str = "unknown") -> dict:
        now = time.time()
        if (
            self._cached_info is not None
            and (now - self._cached_time) < self._cache_ttl
        ):
            return self._cached_info

        headers = {"X-Request-ID": request_id}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            res = await client.get(f"{self.base_url}/model-info", headers=headers)
            res.raise_for_status()
            data = res.json()
            self._cached_info = data
            self._cached_time = now
            return data

    async def predict(self, values: dict, request_id: str = "unknown") -> dict:
        headers = {"X-Request-ID": request_id}
        # One retry after connection error (per backend.md section 7.5)
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    res = await client.post(
                        f"{self.base_url}/predict", json=values, headers=headers
                    )
                    res.raise_for_status()
                    return res.json()
            except httpx.ConnectError:
                if attempt == 0:
                    continue
                raise
