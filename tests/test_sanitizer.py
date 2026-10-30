import sys
import os

# Add repo to sys.path
sys.path.insert(0, os.path.abspath("."))

from src.core.security.sanitizer import DataSanitizer
from src.core.models import Incident, AlertSeverity

def test_sanitizer():
    sample_text = (
        "Error in checkout user 19.876.543-k with email juan.perez@empresa.cl and IP 200.54.12.89. "
        "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.token123.sig456 with api_key=secret_xyz987654321 and card 4532-1234-5678-9010."
    )
    
    clean = DataSanitizer.sanitize_text(sample_text)
    print("=== ORIGINAL ===")
    print(sample_text)
    print("\n=== SANITIZED ===")
    print(clean)
    
    assert "[RUT_PROTEGIDO]" in clean, "RUT was not masked!"
    assert "[EMAIL_PROTEGIDO]" in clean, "Email was not masked!"
    assert "[IP_PUBLICA_PROTEGIDA]" in clean, "Public IP was not masked!"
    assert "[JWT_TOKEN_OCULTO]" in clean or "[TOKEN_OCULTO]" in clean, "Token was not masked!"
    assert "[TARJETA_PROTEGIDA]" in clean, "Credit card was not masked!"
    print("\n[OK] All sanitization tests passed successfully!")

if __name__ == "__main__":
    test_sanitizer()
