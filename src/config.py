import json
from typing import List, Optional, Dict, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class TargetConfig(BaseSettings):
    name: str
    url: str
    interval_seconds: int = 60
    expected_status: int = 200
    timeout_seconds: float = 10.0


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # System & Security
    APP_NAME: str = "GMA-DEV"
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "INFO"
    AUDIT_LOG_PATH: str = "audit_logs/incidents.jsonl"
    MASK_PII_ENABLED: bool = True

    # Server
    PORT: int = 8080
    HOST: str = "0.0.0.0"
    WEBHOOK_SECRET: Optional[str] = None

    # Discord
    DISCORD_ENABLED: bool = False
    DISCORD_WEBHOOK_URL: Optional[str] = None

    # Telegram
    TELEGRAM_ENABLED: bool = False
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    # WhatsApp
    WHATSAPP_ENABLED: bool = False
    WHATSAPP_PROVIDER: str = "meta"  # 'meta' or 'twilio'
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_ACCESS_TOKEN: Optional[str] = None
    WHATSAPP_RECIPIENT_PHONE: Optional[str] = None
    WHATSAPP_TEMPLATE_NAME: str = "incident_alert_v1"
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_FROM: Optional[str] = None

    # Microsoft Clarity
    CLARITY_ENABLED: bool = False
    CLARITY_API_TOKEN: Optional[str] = None
    CLARITY_PROJECT_ID: Optional[str] = None
    CLARITY_CHECK_INTERVAL_MINUTES: int = 60

    # Monitored Targets
    MONITORED_TARGETS: str = "[]"

    # AI Plugins
    AI_ENRICHER_ENABLED: bool = False
    AI_PROVIDER: str = "ollama"  # 'ollama', 'openai', 'gemini'
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    def get_parsed_targets(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.MONITORED_TARGETS)
        except Exception:
            return []


settings = Settings()
