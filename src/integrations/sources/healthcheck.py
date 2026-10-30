import time
import httpx
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timezone
from src.core.models import Incident, AlertSeverity

logger = logging.getLogger("HealthcheckSource")


class HealthcheckMonitor:
    """
    Proactive, non-invasive healthcheck monitor compliant with Ley 21.459.
    Monitors web service availability, latency, and status code transitions.
    """

    def __init__(self):
        # In-memory state tracking: {target_name: {"is_up": bool, "last_check": float, "last_status": int}}
        self._state: Dict[str, Dict] = {}

    async def check_target(self, name: str, url: str, expected_status: int = 200, timeout_seconds: float = 10.0) -> Tuple[bool, Optional[Incident]]:
        start_time = time.perf_counter()
        is_up = False
        status_code = None
        error_msg = None

        try:
            async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
                response = await client.get(url, headers={"User-Agent": "OpsSentinel-Healthcheck/1.0 (+https://github.com/ops-sentinel)"})
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                status_code = response.status_code
                is_up = (status_code == expected_status)
                if not is_up:
                    error_msg = f"Unexpected HTTP status {status_code} (expected {expected_status})"
        except httpx.TimeoutException:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            error_msg = f"Connection timed out after {timeout_seconds}s"
        except httpx.RequestError as exc:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            error_msg = f"Network/DNS error: {str(exc)}"
        except Exception as exc:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            error_msg = f"Unexpected check failure: {str(exc)}"

        previous_state = self._state.get(name, {"is_up": True})
        was_up = previous_state.get("is_up", True)
        self._state[name] = {"is_up": is_up, "last_check": time.time(), "last_status": status_code}

        incident = None

        # State transition: UP -> DOWN
        if was_up and not is_up:
            incident = Incident(
                id=f"hc-down-{name.lower().replace(' ', '-')}-{int(time.time())}",
                service_name=name,
                severity=AlertSeverity.CRITICAL,
                title=f"Service Down: {name}",
                description=f"Healthcheck failed for {name}. Error: {error_msg}. Latency: {latency_ms}ms.",
                status_code=status_code,
                response_time_ms=latency_ms,
                endpoint=url,
                metadata={"error_details": error_msg}
            )

        # State transition: DOWN -> UP (Recovery)
        elif not was_up and is_up:
            incident = Incident(
                id=f"hc-recov-{name.lower().replace(' ', '-')}-{int(time.time())}",
                service_name=name,
                severity=AlertSeverity.RESOLVED,
                title=f"Service Recovered: {name}",
                description=f"Service {name} is back online with HTTP {status_code}. Latency: {latency_ms}ms.",
                status_code=status_code,
                response_time_ms=latency_ms,
                endpoint=url
            )

        return is_up, incident
