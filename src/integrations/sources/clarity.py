import httpx
import logging
from typing import Optional
from datetime import datetime, timezone
from src.core.models import ClarityMetrics, Incident, AlertSeverity, IncidentEvidence
from src.config import settings

logger = logging.getLogger("ClaritySource")


class ClarityClient:
    """
    Microsoft Clarity API Integration.
    Fetches behavioral and error telemetry (rage clicks, dead clicks, JS errors, active sessions)
    to detect UX degradation and silent frontend/API failures.
    """

    BASE_URL = "https://www.clarity.ms/export-data/api/v1"

    def __init__(self, api_token: Optional[str] = None, project_id: Optional[str] = None):
        self.api_token = api_token or settings.CLARITY_API_TOKEN
        self.project_id = project_id or settings.CLARITY_PROJECT_ID

    async def fetch_metrics(self) -> Optional[ClarityMetrics]:
        if not self.api_token or not self.project_id:
            logger.warning("Microsoft Clarity is enabled but API_TOKEN or PROJECT_ID is missing.")
            return None

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        # Microsoft Clarity data export endpoint for project analytics
        url = f"{self.BASE_URL}/project-live-insights/{self.project_id}"

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    # Parse telemetry safely
                    metrics = ClarityMetrics(
                        project_id=self.project_id,
                        timestamp=datetime.now(timezone.utc),
                        total_sessions=data.get("totalSessions", 0),
                        active_users=data.get("activeUsers", 0),
                        rage_clicks=data.get("rageClicks", 0),
                        dead_clicks=data.get("deadClicks", 0),
                        excessive_scrolls=data.get("excessiveScrolls", 0),
                        js_errors=data.get("javascriptErrors", 0),
                        pages_with_errors=data.get("topPagesWithErrors", [])
                    )
                    return metrics
                elif response.status_code == 401:
                    logger.error("Microsoft Clarity authentication failed: Invalid API Token.")
                    return None
                else:
                    logger.warning(f"Microsoft Clarity returned status {response.status_code}: {response.text}")
                    # Return fallback metric snapshot if API response structure varies
                    return None
        except Exception as e:
            logger.error(f"Error fetching telemetry from Microsoft Clarity: {str(e)}")
            return None

    def evaluate_anomalies(self, metrics: ClarityMetrics) -> Optional[Incident]:
        """
        Detects silent frontend breakdowns (e.g. broken checkout, unresponsive buttons).
        Triggers an Incident when rage clicks or JS errors exceed operational thresholds.
        """
        # Threshold: > 20 rage clicks or > 15 JS errors in a sampling window
        if metrics.rage_clicks > 25 or metrics.js_errors > 20:
            return Incident(
                id=f"clarity-anomaly-{int(metrics.timestamp.timestamp())}",
                service_name="Frontend UX (Microsoft Clarity)",
                severity=AlertSeverity.WARNING,
                title="Spike in Frontend UX Friction / JavaScript Errors",
                description=(
                    f"Microsoft Clarity detected abnormal friction in user sessions: "
                    f"{metrics.rage_clicks} rage clicks, {metrics.dead_clicks} dead clicks, and {metrics.js_errors} JS errors. "
                    f"Affected pages: {', '.join(metrics.pages_with_errors[:3]) if metrics.pages_with_errors else 'Global'}"
                ),
                metadata={
                    "total_sessions": metrics.total_sessions,
                    "active_users": metrics.active_users,
                    "rage_clicks": metrics.rage_clicks,
                    "dead_clicks": metrics.dead_clicks,
                    "js_errors": metrics.js_errors
                },
                evidence=IncidentEvidence(
                    attack_vector="Client-Side Exception / UX Rage Clicks Spike",
                    clarity_session_url=f"https://clarity.ms/projects/view/{self.project_id}/dashboard"
                )
            )
        return None
