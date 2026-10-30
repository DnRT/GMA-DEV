import httpx
import logging
from typing import Optional
from src.core.models import Incident, ReportSummary, AlertSeverity
from src.integrations.channels.base import NotificationChannel
from src.config import settings

logger = logging.getLogger("DiscordChannel")


class DiscordChannel(NotificationChannel):
    """
    Discord Webhook Notification Channel.
    Uses Rich Embeds with color-coded severity states and structured metrics.
    """

    COLOR_MAP = {
        AlertSeverity.CRITICAL: 15158332,  # Red #E74C3C
        AlertSeverity.WARNING: 15964690,   # Amber #F39C12
        AlertSeverity.RESOLVED: 3066993,   # Green #2ECC71
        AlertSeverity.INFO: 3447003        # Blue #3498DB
    }

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or settings.DISCORD_WEBHOOK_URL

    @property
    def name(self) -> str:
        return "discord"

    async def send_incident(self, incident: Incident) -> bool:
        if not self.webhook_url:
            return False

        color = self.COLOR_MAP.get(incident.severity, 3447003)
        fields = [
            {"name": "Service", "value": f"`{incident.service_name}`", "inline": True},
            {"name": "Severity", "value": f"**{incident.severity.value}**", "inline": True},
        ]

        if incident.status_code:
            fields.append({"name": "HTTP Status", "value": f"`{incident.status_code}`", "inline": True})
        if incident.response_time_ms is not None:
            fields.append({"name": "Latency", "value": f"`{incident.response_time_ms} ms`", "inline": True})
        if incident.endpoint:
            fields.append({"name": "Endpoint", "value": f"`{incident.endpoint}`", "inline": False})
        if incident.ai_analysis:
            fields.append({"name": "🤖 AI Incident Analysis", "value": incident.ai_analysis, "inline": False})

        embed = {
            "title": f"🚨 {incident.title}",
            "description": incident.description,
            "color": color,
            "fields": fields,
            "timestamp": incident.timestamp.isoformat(),
            "footer": {
                "text": f"OpsSentinel • Incident ID: {incident.id} • Ley 21.663 Compliant"
            }
        }

        payload = {
            "username": "OpsSentinel AlertManager",
            "embeds": [embed]
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(self.webhook_url, json=payload)
                return res.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Failed to deliver Discord incident alert: {str(e)}")
            return False

    async def send_report(self, report: ReportSummary) -> bool:
        if not self.webhook_url:
            return False

        fields = [
            {"name": "Uptime SLA", "value": f"**{report.uptime_percentage:.2f}%**", "inline": True},
            {"name": "Total Incidents", "value": f"`{report.total_incidents}`", "inline": True},
            {"name": "Critical Incidents", "value": f"`{report.critical_incidents}`", "inline": True},
        ]

        if report.mean_time_to_recovery_seconds is not None:
            fields.append({
                "name": "MTTR (Mean Time to Recovery)",
                "value": f"`{report.mean_time_to_recovery_seconds / 60:.1f} mins`",
                "inline": True
            })

        if report.clarity_metrics:
            cm = report.clarity_metrics
            clarity_text = (
                f"• Active Users: `{cm.active_users}`\n"
                f"• Rage Clicks: `{cm.rage_clicks}` | Dead Clicks: `{cm.dead_clicks}`\n"
                f"• JavaScript Errors: `{cm.js_errors}`"
            )
            fields.append({"name": "📊 Microsoft Clarity UX Stats", "value": clarity_text, "inline": False})

        embed = {
            "title": f"📈 {report.title}",
            "color": 3066993 if report.critical_incidents == 0 else 15964690,
            "fields": fields,
            "timestamp": report.period_end.isoformat(),
            "footer": {"text": "OpsSentinel Periodic System Health Report"}
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(self.webhook_url, json={"username": "OpsSentinel Reporter", "embeds": [embed]})
                return res.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Failed to deliver Discord report: {str(e)}")
            return False
