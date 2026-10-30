import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any
from src.core.models import Incident
from src.config import settings


class AuditLogger:
    """
    Immutable, append-only audit logger compliant with Chilean Ley 21.663.
    Provides verifiable traceability of security incidents, status changes,
    and administrative alerts for CSIRT/ANCI reporting.
    """

    def __init__(self, log_path: str = None):
        self.log_path = log_path or settings.AUDIT_LOG_PATH
        self._ensure_log_directory()

    def _ensure_log_directory(self):
        log_dir = os.path.dirname(self.log_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

    def _compute_hash(self, entry: Dict[str, Any]) -> str:
        serialized = json.dumps(entry, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def record_incident(self, incident: Incident, action: str = "INCIDENT_DETECTED"):
        timestamp_utc = datetime.now(timezone.utc).isoformat()
        
        record = {
            "timestamp": timestamp_utc,
            "incident_id": incident.id,
            "service_name": incident.service_name,
            "severity": incident.severity.value,
            "action": action,
            "title": incident.title,
            "status_code": incident.status_code,
            "response_time_ms": incident.response_time_ms,
            "endpoint": incident.endpoint,
            "metadata": incident.metadata
        }
        
        # Calculate checksum for entry integrity
        record["entry_sha256"] = self._compute_hash(record)

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def record_event(self, event_type: str, details: Dict[str, Any]):
        timestamp_utc = datetime.now(timezone.utc).isoformat()
        record = {
            "timestamp": timestamp_utc,
            "event_type": event_type,
            "details": details
        }
        record["entry_sha256"] = self._compute_hash(record)

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


audit_logger = AuditLogger()
