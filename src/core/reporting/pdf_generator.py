import os
import io
from typing import Dict, Any
from markdown_pdf import MarkdownPdf, Section

ENTERPRISE_CSS = """
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: #1e293b;
}
h1 {
    color: #0f172a;
    font-size: 16pt;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 6px;
    margin-top: 14pt;
}
h2 {
    color: #1e293b;
    font-size: 12pt;
    margin-top: 12pt;
    margin-bottom: 4pt;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 10pt 0;
    font-size: 9pt;
}
th, td {
    border: 1px solid #cbd5e1;
    padding: 5pt 7pt;
    text-align: left;
}
th {
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: bold;
}
tr:nth-child(even) {
    background-color: #f8fafc;
}
code {
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 1pt 3pt;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 8.5pt;
    border-radius: 2px;
}
pre {
    background-color: #0f172a;
    color: #f8fafc;
    padding: 6pt;
    border-radius: 4px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 8pt;
}
blockquote {
    border-left: 3px solid #0284c7;
    margin: 8pt 0;
    padding-left: 8pt;
    color: #475569;
    font-style: italic;
}
"""


def generate_pdf_for_incident(dossier: Dict[str, Any]) -> bytes:
    incident_id = dossier.get("incident_id", "INC-UNKNOWN")
    service_name = dossier.get("service_name", "Web Service")
    severity = dossier.get("severity", "WARNING")
    title = dossier.get("title", "Alerta Operativa")
    description = dossier.get("description", "Sin descripcion")
    timestamp = dossier.get("timestamp", "")
    endpoint = dossier.get("endpoint") or "N/A"
    status_code = dossier.get("status_code") or "N/A"
    latency = dossier.get("response_time_ms") or 0.0
    evidence = dossier.get("evidence") or {}
    source_ip = evidence.get("source_ip") or "N/A"
    attack_vector = evidence.get("attack_vector") or "N/A"
    clarity_url = evidence.get("clarity_session_url") or "https://clarity.microsoft.com"
    payload = evidence.get("raw_payload_snippet") or "N/A"
    sha256 = dossier.get("entry_sha256") or "N/A"

    # Branch 1: Security Incident (ANCI / CSIRT Dossier)
    if "SEC" in incident_id or "Ataque" in title or "Intrusion" in title:
        md = f"""# EXPEDIENTE OFICIAL DE INCIDENTE DE CIBERSEGURIDAD
## NOTIFICACIÓN CSIRT NACIONAL / AGENCIA NACIONAL DE CIBERSEGURIDAD (ANCI)
### Conforme a la Ley Marco de Ciberseguridad (Ley Nº 21.663)

---

**ESTADO DEL EXPEDIENTE:** `NOTIFICACIÓN PRELIMINAR (PLAZO 3 HORAS)`  
**CÓDIGO DE INCIDENTE GMA-DEV:** `{incident_id}`  
**SEVERIDAD:** `{severity}`  
**MARCA TEMPORAL (UTC):** `{timestamp}`  

---

## 1. IDENTIFICACIÓN Y TAXONOMÍA
* **Servicio Afectado:** `{service_name}`
* **Categoría CSIRT:** `Intrusión Web / Código Malicioso`
* **Vector de Ataque:** `{attack_vector}`
* **Endpoint / URL:** `{endpoint}`

---

## 2. EVIDENCIA TÉCNICA E INDICADORES DE COMPROMISO (IOCs)
| Campo | Detalle Técnico Recuperado de Bóveda |
| :--- | :--- |
| **IP Origen del Atacante:** | `{source_ip}` |
| **Código HTTP / Latencia:** | `HTTP {status_code} | {latency} ms` |
| **Fragmento Payload:** | `{payload}` |
| **Firma Criptográfica SHA-256:** | `{sha256}` |

---

## 3. TELEMETRÍA DE COMPORTAMIENTO (MICROSOFT CLARITY)
* **Grabación de Sesión del Incidente:** [{clarity_url}]({clarity_url})

---

## 4. MEDIDAS DE CONTENCIÓN Y MITIGACIÓN APLICADAS
1. Bloqueo perimetral de la dirección IP atacante `{source_ip}` en Firewall de borde.
2. Sanitización estricta de parámetros en endpoint `{endpoint}`.
3. Sellado inmutable del registro para trazabilidad probatoria ante la fiscalía y ANCI.

---
*Expediente generado automáticamente por GMA-DEV (Get My Alert, Developer) • Ley 21.663 Compliant*
"""

    # Branch 2: Clarity UX Incident
    elif "CLARITY" in incident_id or "Rage Clicks" in title:
        md = f"""# EXPEDIENTE DE INVESTIGACIÓN UX & FRICCIÓN EN CLIENTE
## TELEMETRÍA DE COMPORTAMIENTO FRONTEND (MICROSOFT CLARITY)

---

**ID DE INCIDENTE:** `{incident_id}`  
**SERVICIO AFECTADO:** `{service_name}`  
**ESTADO:** `INVESTIGACIÓN ACTIVA`  
**FECHA Y HORA:** `{timestamp}`  

---

## 1. RESUMEN DE LA ANOMALÍA
{description}

* **Endpoint / Página Afectada:** `{endpoint}`
* **Estado HTTP del Servidor:** `HTTP {status_code} (Servidor respondiendo normalmente)`
* **Vector de Fricción:** `{attack_vector}`

---

## 2. EVIDENCIA DE COMPORTAMIENTO (SESIÓN GRABADA)
Para visualizar la reproducción exacta de la pantalla del usuario donde ocurrió el bloqueo:
* **Enlace de Reproducción Clarity:** [{clarity_url}]({clarity_url})

---

## 3. PLAN DE ACCIÓN RECOMENDADO
1. Revisar eventos `onClick` en componentes interactivos de `{endpoint}`.
2. Confirmar que librerías externas o scripts de analítica no bloqueen el hilo principal de renderizado.
"""

    # Branch 3: Infrastructure Outage / Crash
    else:
        md = f"""# INFORME POST-MORTEM & ANÁLISIS DE CAUSA RAÍZ (RCA)
## DISPONIBILIDAD OPERATIVA Y CUMPLIMIENTO DE SLA

---

**ID DE INCIDENTE:** `{incident_id}`  
**SERVICIO AFECTADO:** `{service_name}`  
**SEVERIDAD:** `{severity}`  
**FECHA Y HORA:** `{timestamp}`  

---

## 1. RESUMEN DEL FALLO
{description}

* **Endpoint Monitoreado:** `{endpoint}`
* **Código HTTP Recibido:** `HTTP {status_code}`
* **Latencia Registrada:** `{latency} ms`

---

## 2. LÍNEA DE TIEMPO Y RECUPERACIÓN
* El sistema GMA-DEV detectó la falla inmediatamente en la verificación periódica de salud.
* Alerta despachada a canales de guardia en tiempo real.
* Integridad del incidente sellada con hash: `{sha256}`.
"""

    styled_md = f"<style>{ENTERPRISE_CSS}</style>\n\n{md}"
    pdf = MarkdownPdf(toc_level=2)
    pdf.add_section(Section(styled_md, paper_size="A4"))
    buf = io.BytesIO()
    pdf.save_bytes(buf)
    return buf.getvalue()
