import html
import httpx
import logging
from typing import Optional
from src.core.models import Incident, ReportSummary, AlertSeverity
from src.integrations.channels.base import NotificationChannel
from src.config import settings

logger = logging.getLogger("TelegramChannel")


class TelegramChannel(NotificationChannel):
    """
    Telegram Bot API Notification Channel.
    Sends lightweight, high-urgency notifications formatted in HTML with mobile-friendly typography.
    """

    SEVERITY_EMOJI = {
        AlertSeverity.CRITICAL: "🔴",
        AlertSeverity.WARNING: "🟡",
        AlertSeverity.RESOLVED: "🟢",
        AlertSeverity.INFO: "🔵"
    }

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or settings.TELEGRAM_CHAT_ID

    @property
    def name(self) -> str:
        return "telegram"

    async def send_incident(self, incident: Incident) -> bool:
        if not self.bot_token or not self.chat_id:
            return False

        emoji = self.SEVERITY_EMOJI.get(incident.severity, "ℹ️")
        safe_title = html.escape(incident.title)
        safe_desc = html.escape(incident.description)
        safe_svc = html.escape(incident.service_name)

        msg_lines = [
            f"{emoji} <b>[{incident.severity.value}] {safe_title}</b>",
            "",
            f"<b>Service:</b> <code>{safe_svc}</code>",
            f"<b>Details:</b> {safe_desc}"
        ]

        if incident.status_code:
            msg_lines.append(f"<b>HTTP Status:</b> <code>{incident.status_code}</code>")
        if incident.response_time_ms is not None:
            msg_lines.append(f"<b>Latency:</b> <code>{incident.response_time_ms} ms</code>")
        if incident.endpoint:
            msg_lines.append(f"<b>Endpoint:</b> <code>{html.escape(incident.endpoint)}</code>")
        if incident.evidence and incident.evidence.source_ip:
            msg_lines.append(f"<b>Source IP:</b> <code>{html.escape(incident.evidence.source_ip)}</code>")
        if incident.evidence and incident.evidence.attack_vector:
            msg_lines.append(f"<b>Vector:</b> <code>{html.escape(incident.evidence.attack_vector)}</code>")
        if incident.evidence and incident.evidence.clarity_session_url:
            msg_lines.append(f'🎥 <a href="{html.escape(incident.evidence.clarity_session_url)}">Ver Sesión en Microsoft Clarity</a>')
        if incident.dossier_url:
            msg_lines.append(f'🛡️ <a href="{html.escape(incident.dossier_url)}">Descargar Expediente ANCI / CSIRT (Ley 21.663)</a>')
        if incident.ai_analysis:
            msg_lines.append("")
            msg_lines.append(f"🤖 <b>AI Diagnostic:</b> <i>{html.escape(incident.ai_analysis)}</i>")

        msg_lines.append("")
        msg_lines.append(f"🏷 <i>ID: {incident.id} | OpsSentinel</i>")

        text = "\n".join(msg_lines)
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                return res.status_code == 200
        except Exception as e:
            logger.error(f"Failed to deliver Telegram incident alert: {str(e)}")
            return False

    async def send_report(self, report: ReportSummary) -> bool:
        if not self.bot_token or not self.chat_id:
            return False

        msg_lines = [
            f"📊 <b>{html.escape(report.title)}</b>",
            "",
            f"• <b>Uptime SLA:</b> <code>{report.uptime_percentage:.2f}%</code>",
            f"• <b>Total Incidents:</b> <code>{report.total_incidents}</code>",
            f"• <b>Critical Incidents:</b> <code>{report.critical_incidents}</code>"
        ]

        if report.mean_time_to_recovery_seconds is not None:
            msg_lines.append(f"• <b>MTTR:</b> <code>{report.mean_time_to_recovery_seconds / 60:.1f} min</code>")

        if report.clarity_metrics:
            cm = report.clarity_metrics
            msg_lines.append("")
            msg_lines.append("<b>Microsoft Clarity UX Metrics:</b>")
            msg_lines.append(f"• Active Users: <code>{cm.active_users}</code>")
            msg_lines.append(f"• Rage Clicks: <code>{cm.rage_clicks}</code> | Dead Clicks: <code>{cm.dead_clicks}</code>")
            msg_lines.append(f"• JS Errors: <code>{cm.js_errors}</code>")

        text = "\n".join(msg_lines)
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                return res.status_code == 200
        except Exception as e:
            logger.error(f"Failed to deliver Telegram report: {str(e)}")
            return False
