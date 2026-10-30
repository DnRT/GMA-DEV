import sys
import os

sys.path.insert(0, os.path.abspath("."))

from src.core.models import Incident, AlertSeverity, IncidentEvidence
from src.core.security.sanitizer import DataSanitizer
from src.core.audit.audit_logger import AuditLogger

def test_anci_vault():
    test_log_path = "tests/test_audit.jsonl"
    if os.path.exists(test_log_path):
        os.remove(test_log_path)

    logger = AuditLogger(log_path=test_log_path)

    raw_evidence = IncidentEvidence(
        source_ip="185.220.101.5",
        attack_vector="SQL Injection / Authorization Bypass",
        raw_payload_snippet="' OR '1'='1' -- admin pass",
        clarity_session_url="https://clarity.ms/projects/view/proj123/recordings/rec456"
    )

    incident = Incident(
        id="inc-sec-test-01",
        service_name="Auth Service",
        severity=AlertSeverity.CRITICAL,
        title="Unauthorized root login attempt",
        description="Intrusion attempt from IP 185.220.101.5 targeting RUT 17.654.321-k",
        evidence=raw_evidence
    )

    # 1. Test Chat Sanitization (Pointer Pattern)
    clean_incident = DataSanitizer.sanitize_incident(incident)
    
    # In chat, IP in evidence must be masked
    assert clean_incident.evidence.source_ip == "[IP_REGISTRADA_EN_EXPEDIENTE_ANCI]", f"Evidence IP was not masked: {clean_incident.evidence.source_ip}"
    # In chat, RUT in description must be masked
    assert "[RUT_PROTEGIDO]" in clean_incident.description, f"RUT in description was not masked: {clean_incident.description}"
    # Clarity session URL must be preserved
    assert clean_incident.evidence.clarity_session_url == "https://clarity.ms/projects/view/proj123/recordings/rec456"

    # 2. Test Forensic Vault (Audit Logger)
    logger.record_incident(clean_incident, raw_evidence=raw_evidence)

    # 3. Retrieve ANCI Dossier from Vault
    dossier = logger.get_incident_dossier("inc-sec-test-01")
    assert dossier is not None, "Dossier could not be retrieved from audit vault"
    assert dossier["evidence"]["source_ip"] == "185.220.101.5", f"Real IP was lost in vault: {dossier['evidence']['source_ip']}"
    assert dossier["evidence"]["clarity_session_url"] == "https://clarity.ms/projects/view/proj123/recordings/rec456"
    assert "entry_sha256" in dossier, "Integrity SHA256 was not generated"

    # Cleanup
    if os.path.exists(test_log_path):
        os.remove(test_log_path)

    print("[OK] ANCI Forensic Vault and Sanitization verified successfully!")

if __name__ == "__main__":
    test_anci_vault()
