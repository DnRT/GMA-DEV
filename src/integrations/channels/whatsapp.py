import os
import json
import httpx
import logging
from typing import Optional, Set
from src.core.models import Incident, ReportSummary, AlertSeverity
from src.integrations.channels.base import NotificationChannel
from src.config import settings

logger = logging.getLogger("WhatsAppChannel")


class WhatsAppChannel(NotificationChannel):
    """
    WhatsApp Notification Channel with Dynamic Recipient Management.
    Supports Meta Cloud API and Twilio with zero-hardcoding via dynamic subscriber vault.
    """

    def __init__(self):
        self.provider = settings.WHATSAPP_PROVIDER.lower()
        self.meta_phone_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.meta_token = settings.WHATSAPP_ACCESS_TOKEN
        self.static_recipient = settings.WHATSAPP_RECIPIENT_PHONE
        self.template_name = settings.WHATSAPP_TEMPLATE_NAME

        # Twilio credentials
        self.twilio_sid = settings.TWILIO_ACCOUNT_SID
        self.twilio_token = settings.TWILIO_AUTH_TOKEN
        self.twilio_from = settings.TWILIO_WHATSAPP_FROM

        self.subscribers_file = os.path.join(
            os.path.dirname(settings.AUDIT_LOG_PATH), "whatsapp_subscribers.json"
        )
        self._ensure_storage()

    @property
    def name(self) -> str:
        return "whatsapp"

    def _ensure_storage(self):
        storage_dir = os.path.dirname(self.subscribers_file)
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir, exist_ok=True)
        if not os.path.exists(self.subscribers_file):
            with open(self.subscribers_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def get_subscribers(self) -> Set[str]:
        subscribers = set()
        if self.static_recipient:
            subscribers.add(self.static_recipient.strip())
        try:
            if os.path.exists(self.subscribers_file):
                with open(self.subscribers_file, "r", encoding="utf-8") as f:
                    subscribers.update(json.load(f))
        except Exception as e:
            logger.error(f"Error reading WhatsApp subscribers: {e}")
        return subscribers

    def add_subscriber(self, phone: str):
        subscribers = self.get_subscribers()
        clean_phone = phone.strip()
        subscribers.add(clean_phone)
        try:
            with open(self.subscribers_file, "w", encoding="utf-8") as f:
                json.dump(list(subscribers), f, indent=2)
            logger.info(f"WhatsApp recipient added: {clean_phone}")
        except Exception as e:
            logger.error(f"Error saving WhatsApp subscriber: {e}")

    async def send_incident(self, incident: Incident) -> bool:
        if not settings.WHATSAPP_ENABLED:
            return False

        recipients = self.get_subscribers()
        if not recipients:
            logger.warning("WhatsApp channel active but no recipients registered.")
            return False

        message_body = (
            f"🚨 *[GMA-DEV] {incident.severity.value}: {incident.service_name}*\n\n"
            f"{incident.title}\n"
            f"Details: {incident.description}\n"
            f"Status: {incident.status_code or 'N/A'} | Latency: {incident.response_time_ms or 0}ms\n"
        )
        if incident.evidence and incident.evidence.source_ip:
            message_body += f"Origen: {incident.evidence.source_ip}\n"
        if incident.dossier_url:
            message_body += f"Expediente ANCI: {incident.dossier_url}\n"
        message_body += f"Ref ID: {incident.id}"

        success = False
        for phone in recipients:
            if self.provider == "meta":
                if await self._send_via_meta_cloud_api(message_body, phone):
                    success = True
            elif self.provider == "twilio":
                if await self._send_via_twilio(message_body, phone):
                    success = True

        return success

    async def _send_via_meta_cloud_api(self, text: str, recipient: str) -> bool:
        if not self.meta_phone_id or not self.meta_token:
            logger.error("Meta WhatsApp Cloud API credentials missing.")
            return False

        url = f"https://graph.facebook.com/v19.0/{self.meta_phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.meta_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient.replace("+", "").strip(),
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text
            }
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                return res.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Meta WhatsApp dispatch exception: {str(e)}")
            return False

    async def _send_via_twilio(self, text: str, recipient: str) -> bool:
        if not self.twilio_sid or not self.twilio_token or not self.twilio_from:
            logger.error("Twilio credentials missing for WhatsApp dispatch.")
            return False

        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
        data = {
            "From": f"whatsapp:{self.twilio_from}",
            "To": f"whatsapp:{recipient}",
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
        if not settings.WHATSAPP_ENABLED:
            return False

        recipients = self.get_subscribers()
        if not recipients:
            return False

        report_body = (
            f"📈 *[GMA-DEV] Reporte Periódico de Salud*\n\n"
            f"• Uptime SLA: *{report.uptime_percentage:.2f}%*\n"
            f"• Total Incidentes: {report.total_incidents}\n"
            f"• Críticos: {report.critical_incidents}\n"
        )
        if report.clarity_metrics:
            cm = report.clarity_metrics
            report_body += f"• Sesiones Clarity: {cm.total_sessions} (Rage clicks: {cm.rage_clicks}, JS Errors: {cm.js_errors})\n"

        success = False
        for phone in recipients:
            if self.provider == "meta":
                if await self._send_via_meta_cloud_api(report_body, phone):
                    success = True
            else:
                if await self._send_via_twilio(report_body, phone):
                    success = True
        return success
