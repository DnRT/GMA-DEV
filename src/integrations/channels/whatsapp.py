import httpx
import logging
from typing import Optional
from src.core.models import Incident, ReportSummary, AlertSeverity
from src.integrations.channels.base import NotificationChannel
from src.config import settings

logger = logging.getLogger("WhatsAppChannel")


class WhatsAppChannel(NotificationChannel):
    """
    WhatsApp Notification Channel.
    Supports official Meta Cloud API (WhatsApp Business Graph API)
    with a pluggable fallback to Twilio Programmable Messaging.
    """

    def __init__(self):
        self.provider = settings.WHATSAPP_PROVIDER.lower()
        self.meta_phone_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.meta_token = settings.WHATSAPP_ACCESS_TOKEN
        self.recipient_phone = settings.WHATSAPP_RECIPIENT_PHONE
        self.template_name = settings.WHATSAPP_TEMPLATE_NAME

        # Twilio credentials
        self.twilio_sid = settings.TWILIO_ACCOUNT_SID
        self.twilio_token = settings.TWILIO_AUTH_TOKEN
        self.twilio_from = settings.TWILIO_WHATSAPP_FROM

    @property
    def name(self) -> str:
        return "whatsapp"

    async def send_incident(self, incident: Incident) -> bool:
        if not settings.WHATSAPP_ENABLED or not self.recipient_phone:
            return False

        message_body = (
            f"🚨 *[OpsSentinel] {incident.severity.value}: {incident.service_name}*\n\n"
            f"{incident.title}\n"
            f"Details: {incident.description}\n"
            f"Status: {incident.status_code or 'N/A'} | Latency: {incident.response_time_ms or 0}ms\n"
            f"Ref ID: {incident.id}"
        )

        if self.provider == "meta":
            return await self._send_via_meta_cloud_api(message_body, incident)
        elif self.provider == "twilio":
            return await self._send_via_twilio(message_body)
        else:
            logger.error(f"Unknown WhatsApp provider: {self.provider}")
            return False

    async def _send_via_meta_cloud_api(self, text: str, incident: Incident) -> bool:
        if not self.meta_phone_id or not self.meta_token:
            logger.error("Meta WhatsApp Cloud API credentials missing.")
            return False

        url = f"https://graph.facebook.com/v19.0/{self.meta_phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.meta_token}",
            "Content-Type": "application/json"
        }

        # Format as standard text message (if within 24h customer care window)
        # or template message for proactive outbound alerts.
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.recipient_phone.replace("+", "").strip(),
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text
            }
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code in [200, 201]:
                    return True
                else:
                    logger.error(f"Meta WhatsApp API error: {res.status_code} - {res.text}")
                    return False
        except Exception as e:
            logger.error(f"Meta WhatsApp dispatch exception: {str(e)}")
            return False

    async def _send_via_twilio(self, text: str) -> bool:
        if not self.twilio_sid or not self.twilio_token or not self.twilio_from:
            logger.error("Twilio credentials missing for WhatsApp dispatch.")
            return False

        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
        data = {
            "From": f"whatsapp:{self.twilio_from}",
            "To": f"whatsapp:{self.recipient_phone}",
            "Body": text
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, data=data, auth=(self.twilio_sid, self.twilio_token))
                return res.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Twilio WhatsApp dispatch exception: {str(e)}")
            return False

    async def send_report(self, report: ReportSummary) -> bool:
        if not settings.WHATSAPP_ENABLED or not self.recipient_phone:
            return False

        report_body = (
            f"📈 *[OpsSentinel] Reporte Periódico de Salud*\n\n"
            f"• Uptime SLA: *{report.uptime_percentage:.2f}%*\n"
            f"• Total Incidentes: {report.total_incidents}\n"
            f"• Críticos: {report.critical_incidents}\n"
        )
        if report.clarity_metrics:
            cm = report.clarity_metrics
            report_body += f"• Sesiones Clarity: {cm.total_sessions} (Rage clicks: {cm.rage_clicks}, JS Errors: {cm.js_errors})\n"

        if self.provider == "meta":
            return await self._send_via_meta_cloud_api(report_body, None)
        else:
            return await self._send_via_twilio(report_body)
