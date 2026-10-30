import os
import json
import html
import httpx
import logging
from typing import Optional, Set
from src.core.models import Incident, ReportSummary, AlertSeverity
from src.integrations.channels.base import NotificationChannel
from src.config import settings

logger = logging.getLogger("TelegramChannel")


class TelegramChannel(NotificationChannel):
    """
    Telegram Bot API Notification Channel with Dynamic Subscription.
    Allows zero-hardcoding: anyone who sends /start to the bot is automatically
    registered as an active subscriber without needing to configure Chat IDs in .env.
    """

    SEVERITY_EMOJI = {
        AlertSeverity.CRITICAL: "🔴",
        AlertSeverity.WARNING: "🟡",
        AlertSeverity.RESOLVED: "🟢",
        AlertSeverity.INFO: "🔵"
    }

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN
        self.static_chat_id = chat_id or settings.TELEGRAM_CHAT_ID
        self.subscribers_file = os.path.join(
            os.path.dirname(settings.AUDIT_LOG_PATH), "telegram_subscribers.json"
        )
        self.last_update_id = 0
        self._ensure_storage()

    @property
    def name(self) -> str:
        return "telegram"

    def _ensure_storage(self):
        storage_dir = os.path.dirname(self.subscribers_file)
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir, exist_ok=True)
        if not os.path.exists(self.subscribers_file):
            with open(self.subscribers_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _load_persisted_subscribers(self) -> Set[str]:
        try:
            if os.path.exists(self.subscribers_file):
                with open(self.subscribers_file, "r", encoding="utf-8") as f:
                    return set(json.load(f))
        except Exception as e:
            logger.error(f"Error loading telegram subscribers: {e}")
        return set()

    def _save_subscribers(self, subscribers: Set[str]):
        try:
            with open(self.subscribers_file, "w", encoding="utf-8") as f:
                json.dump(list(subscribers), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving telegram subscribers: {e}")

    async def sync_subscribers(self) -> Set[str]:
        """
        Polls Telegram getUpdates API to automatically discover any user or group
        interacting with the bot (/start to subscribe, /stop to unsubscribe).
        """
        subscribers = self._load_persisted_subscribers()

        # If a static ID was provided in .env, preserve it as default
        if self.static_chat_id:
            subscribers.add(str(self.static_chat_id).strip())

        if not self.bot_token:
            return subscribers

        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        params = {"offset": self.last_update_id + 1, "timeout": 2}

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url, params=params)
                if res.status_code == 200:
                    data = res.json()
                    for update in data.get("result", []):
                        self.last_update_id = max(self.last_update_id, update.get("update_id", 0))
                        msg = update.get("message") or update.get("channel_post")
                        if not msg:
                            continue

                        chat = msg.get("chat", {})
                        chat_id = str(chat.get("id"))
                        text = (msg.get("text") or "").strip().lower()

                        if not chat_id:
                            continue

                        # Command /stop or /unsubscribe
                        if text in ["/stop", "/unsubscribe", "stop"]:
                            if chat_id in subscribers:
                                subscribers.remove(chat_id)
                                logger.info(f"Telegram chat unsubscribed: {chat_id}")
                                await self._send_raw_message(
                                    chat_id, "❌ <b>GMA-DEV:</b> Has sido desuscrito de las alertas operativas."
                                )
                        # Any other interaction or /start /subscribe
                        else:
                            if chat_id not in subscribers:
                                subscribers.add(chat_id)
                                logger.info(f"Telegram chat auto-registered: {chat_id}")
                                await self._send_raw_message(
                                    chat_id, "✅ <b>GMA-DEV:</b> Suscripción activa. Recibirás alertas e informes en este chat."
                                )

                    self._save_subscribers(subscribers)
        except Exception as e:
            logger.warning(f"Could not sync dynamic Telegram subscribers: {e}")

        return subscribers

    async def _send_raw_message(self, chat_id: str, text: str) -> bool:
        if not self.bot_token:
            return False
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                return res.status_code == 200
        except Exception:
            return False

    async def send_incident(self, incident: Incident) -> bool:
        if not self.bot_token:
            return False

        # Dynamically discover any user who pressed /start
        recipients = await self.sync_subscribers()
        if not recipients:
            logger.warning("Telegram channel active but no subscribers found. Open the bot and send /start.")
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
        msg_lines.append(f"🏷 <i>ID: {incident.id} | GMA-DEV</i>")

        text = "\n".join(msg_lines)
        success_count = 0
        for chat_id in recipients:
            if await self._send_raw_message(chat_id, text):
                success_count += 1

        return success_count > 0

    async def send_report(self, report: ReportSummary) -> bool:
        if not self.bot_token:
            return False

        recipients = await self.sync_subscribers()
        if not recipients:
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
        success_count = 0
        for chat_id in recipients:
            if await self._send_raw_message(chat_id, text):
                success_count += 1

        return success_count > 0
