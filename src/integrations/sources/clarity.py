import time
import httpx
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from src.core.models import ClarityMetrics, Incident, AlertSeverity, IncidentEvidence
from src.config import settings

logger = logging.getLogger("ClaritySource")


class ClarityClient:
    """
    Microsoft Clarity Data Export API Integration.
    Fetches real-world behavioral and client error telemetry:
    Rage clicks, Dead clicks, Script (JS) errors, and Traffic.
    Includes in-memory TTL caching to respect Microsoft API rate quotas.
    """

    ENDPOINT = "https://www.clarity.ms/export-data/api/v1/project-live-insights"

    def __init__(self, api_token: Optional[str] = None, project_id: Optional[str] = None):
        self.api_token = api_token or settings.CLARITY_API_TOKEN
        self.project_id = project_id or settings.CLARITY_PROJECT_ID
        self._cached_metrics: Optional[ClarityMetrics] = None
        self._cache_timestamp: float = 0.0
        self._cache_ttl_seconds: float = 300.0  # 5 minutes cache to protect quota

    async def fetch_metrics(self) -> Optional[ClarityMetrics]:
        if not self.api_token:
            logger.warning("Microsoft Clarity is enabled but API_TOKEN is missing.")
            return None

        # Return cached metrics if within TTL
        if self._cached_metrics and (time.time() - self._cache_timestamp < self._cache_ttl_seconds):
            return self._cached_metrics

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        params = {"numOfDays": 1}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.ENDPOINT, headers=headers, params=params)

                if response.status_code == 200:
                    data = response.json()
                    metrics = self._parse_clarity_response(data)
                    self._cached_metrics = metrics
                    self._cache_timestamp = time.time()
                    return metrics
                elif response.status_code == 401:
                    logger.error("Microsoft Clarity authentication failed: Invalid or expired API Token.")
                    return None
                elif response.status_code == 429:
                    logger.warning("Microsoft Clarity API quota reached (Daily limit). Using last cached metrics.")
                    return self._cached_metrics
                else:
                    logger.warning(f"Microsoft Clarity returned status {response.status_code}: {response.text}")
                    return self._cached_metrics
        except httpx.TimeoutException:
            logger.warning("Microsoft Clarity API request timed out (30s). Re-trying next cycle.")
            return self._cached_metrics
        except Exception as e:
            logger.error(f"Error fetching telemetry from Microsoft Clarity: {str(e)}")
            return self._cached_metrics

    def _parse_clarity_response(self, data: Any) -> ClarityMetrics:
        metrics_dict: Dict[str, int] = {
            "DeadClickCount": 0,
            "RageClickCount": 0,
            "ScriptErrorCount": 0,
            "ExcessiveScroll": 0,
            "Traffic": 0
        }

        if isinstance(data, list):
            for item in data:
                metric_name = item.get("metricName")
                info_list = item.get("information", [])
                if metric_name in metrics_dict and info_list and isinstance(info_list, list):
                    info_obj = info_list[0] if len(info_list) > 0 else {}
                    sub_total = info_obj.get("subTotal", 0)
                    try:
                        metrics_dict[metric_name] = int(sub_total)
                    except (ValueError, TypeError):
                        pass

        project_id_str = self.project_id or "default"
        return ClarityMetrics(
            project_id=project_id_str,
            timestamp=datetime.now(timezone.utc),
            total_sessions=metrics_dict["Traffic"],
            active_users=metrics_dict["Traffic"],
            rage_clicks=metrics_dict["RageClickCount"],
            dead_clicks=metrics_dict["DeadClickCount"],
            excessive_scrolls=metrics_dict["ExcessiveScroll"],
            js_errors=metrics_dict["ScriptErrorCount"],
            pages_with_errors=[]
        )

    def evaluate_anomalies(self, metrics: ClarityMetrics) -> Optional[Incident]:
        """
        Detects silent frontend breakdowns (e.g. broken checkout, unresponsive buttons).
        Triggers an Incident when rage clicks or JS errors exceed operational thresholds.
        """
        if metrics.rage_clicks > 25 or metrics.js_errors > 20:
            project_id_str = self.project_id or "default"
            return Incident(
                id=f"clarity-anomaly-{int(metrics.timestamp.timestamp())}",
                service_name="Frontend UX (Microsoft Clarity)",
                severity=AlertSeverity.WARNING,
                title="Pico de Rage Clicks / Errores JavaScript en Frontend",
                description=(
                    f"Microsoft Clarity detecto anomalias de experiencia de usuario: "
                    f"{metrics.rage_clicks} rage clicks, {metrics.dead_clicks} dead clicks y {metrics.js_errors} errores JS."
                ),
                metadata={
                    "total_sessions": metrics.total_sessions,
                    "active_users": metrics.active_users,
                    "rage_clicks": metrics.rage_clicks,
                    "dead_clicks": metrics.dead_clicks,
                    "js_errors": metrics.js_errors
                },
                evidence=IncidentEvidence(
                    attack_vector="Client-Side Exception / UX Friction",
                    clarity_session_url=f"https://clarity.ms/projects/view/{project_id_str}/dashboard"
                )
            )
        return None
