import re
from typing import Any, Dict, List, Union
from src.core.models import Incident


class DataSanitizer:
    """
    Mandatory PII & Secret Sanitization Engine.
    Complies with Chilean Ley 21.663 (Security by Design) and Data Privacy Standards (GDPR-aligned).
    Prevents leaking Personal Identifiable Information (PII) and credentials to external chat channels.
    """

    # Chilean National ID (RUT) regex pattern: XX.XXX.XXX-X or XXXXXXXX-X
    RUT_PATTERN = re.compile(r"\b(\d{1,2}(?:\.?\d{3}){2}-?[\dkK])\b", re.IGNORECASE)

    # Email pattern
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

    # IPv4 Pattern
    IPV4_PATTERN = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")

    # Bearer / JWT Tokens / Passwords / API Keys
    AUTH_HEADER_PATTERN = re.compile(r"(?i)(bearer\s+)[a-zA-Z0-9\-_.]+")
    API_KEY_PATTERN = re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd|pwd)[\s:=]+['\"]?([a-zA-Z0-9_\-]{8,})['\"]?")
    JWT_PATTERN = re.compile(r"\beyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b")

    # Credit Card pattern (Visa, MC, Amex)
    CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        if not text or not isinstance(text, str):
            return text

        # 1. Mask Chilean RUT
        text = cls.RUT_PATTERN.sub("[RUT_PROTEGIDO]", text)

        # 2. Mask Emails
        text = cls.EMAIL_PATTERN.sub("[EMAIL_PROTEGIDO]", text)

        # 3. Mask Credit Cards
        text = cls.CREDIT_CARD_PATTERN.sub("[TARJETA_PROTEGIDA]", text)

        # 4. Mask JWT and Bearer tokens
        text = cls.JWT_PATTERN.sub("[JWT_TOKEN_OCULTO]", text)
        text = cls.AUTH_HEADER_PATTERN.sub(r"\1[TOKEN_OCULTO]", text)

        # 5. Mask API keys and passwords
        text = cls.API_KEY_PATTERN.sub(r"\1: [CREDENCIAL_OCULTA]", text)

        # 6. Mask IPv4 (except internal docker/private loopback ranges)
        def replace_ip(match):
            ip = match.group(0)
            if ip.startswith(("127.", "10.", "172.16.", "192.168.", "0.0.0.0")):
                return ip  # allow private/local debugging ranges
            return "[IP_PUBLICA_PROTEGIDA]"

        text = cls.IPV4_PATTERN.sub(replace_ip, text)

        return text

    @classmethod
    def sanitize_data(cls, data: Union[Dict[str, Any], List[Any], str, Any]) -> Any:
        if isinstance(data, str):
            return cls.sanitize_text(data)
        elif isinstance(data, dict):
            sanitized_dict = {}
            for k, v in data.items():
                # Obscure known secret keys completely
                if any(secret_term in k.lower() for secret_term in ["password", "secret", "token", "key", "authorization"]):
                    sanitized_dict[k] = "[DATO_SENSIBLE_RESTRINGIDO]"
                else:
                    sanitized_dict[k] = cls.sanitize_data(v)
            return sanitized_dict
        elif isinstance(data, list):
            return [cls.sanitize_data(item) for item in data]
        return data

    @classmethod
    def sanitize_incident(cls, incident: Incident) -> Incident:
        """Produces a sanitized copy of an Incident object safe for external delivery."""
        clean_dict = incident.model_dump()
        clean_dict["title"] = cls.sanitize_text(incident.title)
        clean_dict["description"] = cls.sanitize_text(incident.description)
        if incident.endpoint:
            clean_dict["endpoint"] = cls.sanitize_text(incident.endpoint)
        if incident.metadata:
            clean_dict["metadata"] = cls.sanitize_data(incident.metadata)
        if incident.ai_analysis:
            clean_dict["ai_analysis"] = cls.sanitize_text(incident.ai_analysis)

        # Sanitize evidence for external chat dispatch (Pointer Pattern)
        if incident.evidence:
            clean_evidence = incident.evidence.model_dump()
            if incident.evidence.source_ip:
                clean_evidence["source_ip"] = "[IP_REGISTRADA_EN_EXPEDIENTE_ANCI]"
            if incident.evidence.raw_payload_snippet:
                clean_evidence["raw_payload_snippet"] = cls.sanitize_text(incident.evidence.raw_payload_snippet)
            clean_dict["evidence"] = clean_evidence

        return Incident(**clean_dict)
