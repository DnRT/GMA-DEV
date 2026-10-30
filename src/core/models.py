from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    RESOLVED = "RESOLVED"


class IncidentEvidence(BaseModel):
    """
    Forensic evidence vault model compliant with Chilean Ley 21.663.
    Preserves raw forensics (attacker IP, vector, payload, Clarity links)
    for official ANCI/CSIRT reporting while keeping chat alerts sanitized.
    """
    source_ip: Optional[str] = None
    attack_vector: Optional[str] = None
    raw_payload_snippet: Optional[str] = None
    clarity_session_url: Optional[str] = None
    integrity_hash: Optional[str] = None


class Incident(BaseModel):
    id: str
    service_name: str
    severity: AlertSeverity
    title: str
    description: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    endpoint: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    ai_analysis: Optional[str] = None
    evidence: Optional[IncidentEvidence] = None
    dossier_url: Optional[str] = None


class ClarityMetrics(BaseModel):
    project_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_sessions: int = 0
    active_users: int = 0
    rage_clicks: int = 0
    dead_clicks: int = 0
    excessive_scrolls: int = 0
    js_errors: int = 0
    pages_with_errors: List[str] = Field(default_factory=list)


class ReportSummary(BaseModel):
    title: str
    period_start: datetime
    period_end: datetime
    uptime_percentage: float
    total_incidents: int
    critical_incidents: int
    mean_time_to_recovery_seconds: Optional[float] = None
    clarity_metrics: Optional[ClarityMetrics] = None
    highlights: List[str] = Field(default_factory=list)
