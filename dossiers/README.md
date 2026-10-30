# Bóveda de Expedientes y Dossiers Oficiales (GMA-DEV)

Este directorio contiene las plantillas y los expedientes oficiales generados en **Markdown (`.md`)** y **PDF listo para imprimir/enviar (`.pdf`)**, estructurados conforme a los requerimientos de la **Ley Marco de Ciberseguridad (Ley Nº 21.663)** y las mejores prácticas de SRE / DevOps.

---

## 📂 Estructura de Directorios

```
dossiers/
├── templates/                             # Plantillas limpias para rellenar
│   ├── TEMPLATE_ANCI_CSIRT_LEY21663.md    # Notificación formal para la ANCI / CSIRT
│   ├── TEMPLATE_POSTMORTEM_INFRAESTRUCTURA.md # Análisis de Causa Raíz (RCA) para caídas
│   └── TEMPLATE_CLARITY_UX_REPORT.md      # Reporte de frustración y errores de frontend
├── samples/                               # Ejemplos reales rellenos con datos de incidentes
│   ├── DOSSIER-INC-SEC-ANCI-CSIRT.md      # Intrusión con IPs reales, IOCs y hashes
│   ├── DOSSIER-INC-CRASH-POSTMORTEM.md    # Caída HTTP 502 y análisis de 5 Porqués
│   └── DOSSIER-INC-CLARITY-UX-REPORT.md   # Pico de Rage Clicks con enlaces a grabaciones
├── pdfs/                                  # Archivos PDF oficiales listos para enviar
│   ├── DOSSIER-INC-SEC-ANCI-CSIRT.pdf
│   ├── DOSSIER-INC-CRASH-POSTMORTEM.pdf
│   └── DOSSIER-INC-CLARITY-UX-REPORT.pdf
└── generate_dossier_pdfs.py               # Compilador automático de Markdown a PDF profesional
```

---

## 🚀 Cómo Usar estos Dossiers en tu Equipo

1. **Para una Notificación Oficial a la ANCI / CSIRT (Plazo 3 Horas):**
   * Copia `templates/TEMPLATE_ANCI_CSIRT_LEY21663.md`.
   * Pega la IP atacante, vector y marcas temporales (obtenidas desde `audit_logs/incidents.jsonl` o el endpoint `/anci-dossier`).
   * Guarda el archivo en `samples/` y compílalo a PDF:
     ```bash
     python dossiers/generate_dossier_pdfs.py
     ```
   * Envía el PDF resultante en `dossiers/pdfs/` a la autoridad.

2. **Para un Post-Mortem de Caída de Servicio (Interno / Clientes):**
   * Utiliza `templates/TEMPLATE_POSTMORTEM_INFRAESTRUCTURA.md`.
   * Documenta la cronología de eventos, métricas de MTTR y los 5 Porqués de la causa raíz.
   * Compila a PDF para presentar a gerencia o al cliente.
