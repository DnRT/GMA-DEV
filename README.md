# GMA-DEV (Get My Alert, Developer)

> **Enterprise-grade, privacy-first ChatOps & Incident Monitoring System.**  
> Built for SysAdmins and DevOps teams managing mission-critical web services with automated notifications via **Discord**, **Telegram**, and **WhatsApp**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Security by Design](https://img.shields.io/badge/Security-Ley_21.663_Compliant-green.svg)](SECURITY.md)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](Dockerfile)
[![Terraform](https://img.shields.io/badge/IaC-Terraform_GCP_%7C_AWS_%7C_Azure-7B42BC?logo=terraform&logoColor=white)](infra/terraform/)

---

## 🏛️ Visión General & Cumplimiento Normativo (Chile & Global)

**GMA-DEV** (*Get My Alert, Developer*) está diseñado bajo el principio estricto de **Seguridad por Defecto y por Diseño (*Security by Design*)**, cumpliendo de forma nativa con los marcos legales vigentes y proyectados:

1. **Ley Marco de Ciberseguridad (Ley Nº 21.663 - Chile):**
   - **Trazabilidad inmutable:** Registro local de auditoría en formato JSON con marcas de tiempo en UTC (`ISO 8601`) para reportes ante la ANCI y CSIRT.
   - **Principio de Mínimo Privilegio:** Ejecución sin privilegios de `root` en contenedores y control estricto de llamadas API.
2. **Ley sobre Delitos Informáticos (Ley Nº 21.459 - Chile / Convenio de Budapest):**
   - Telemetría legítima y no invasiva de endpoints autorizados.
   - Prevención de abuso de dispositivos e inyección de comandos.
3. **Nueva Ley de Protección de Datos Personales (Chile) y GDPR (UE):**
   - **Pipeline de Sanitización Activa:** Enmascara automáticamente antes de notificar:
     - RUT chileno (`XX.XXX.XXX-X`)
     - Correos electrónicos y tarjetas de crédito
     - Tokens de sesión, JWT, Authorization Bearer, Passwords y API Keys
     - Direcciones IP públicas de usuarios finales
   - **Alerta por Puntero (Pointer Alerts):** Solo se despachan resúmenes técnicos abstractos a plataformas de terceros (Discord, Telegram, WhatsApp), evitando la fuga transfronteriza de datos personales.

---

## 🏗️ Arquitectura del Sistema

```mermaid
flowchart TD
    subgraph Fuentes ["Fuentes de Telemetría"]
        A1["Microsoft Clarity API\n(Dead clicks, Rage clicks, UX errors)"]
        A2["Web Services & APIs\n(Healthchecks, Latency, Status 5xx)"]
        A3["Sistemas Externos / Webhooks\n(Prometheus / Uptime / Sentry)"]
    end

    subgraph Core ["GMA-DEV Core (Local o Multi-Cloud)"]
        B1["Ingesta & Evaluador de Incidentes"]
        B2["Pipeline de Sanitización & PII Masking\n(RUT, IPs, Tokens)"]
        B3["Audit Logger Inmutable (UTC / JSON)\n[Ley 21.663]"]
        B4["Motor de Plugins / Extensibilidad\n(AI Enricher: Ollama / OpenAI / Gemini)"]
    end

    subgraph Canales ["Despacho Multicanal Seguro (TLS 1.3)"]
        C1["Discord (Rich Embeds & Color Status)"]
        C2["Telegram (Bot API & Alertas Operativas)"]
        C3["WhatsApp (Meta Cloud API / Twilio Gateway)"]
    end

    A1 --> B1
    A2 --> B1
    A3 --> B1
    B1 --> B2
    B2 --> B3
    B2 --> B4
    B4 --> C1
    B4 --> C2
    B4 --> C3
```

---

## 🚀 Despliegue Multi-Cloud & Resiliencia

GMA-DEV soporta despliegue redundante e híbrido para evitar caídas ante fallos de proveedores de DNS o Cloudflare:

| Entorno | Método de Despliegue | Ubicación de Configuración |
| :--- | :--- | :--- |
| **Local / Bare Metal** | Docker & Docker Compose | [`docker-compose.yml`](docker-compose.yml) |
| **GCP (Google Cloud)** | Terraform (Cloud Run + Secret Manager) | [`infra/terraform/gcp/`](infra/terraform/gcp/) |
| **AWS** | Terraform (ECS Fargate + Secrets Manager) | [`infra/terraform/aws/`](infra/terraform/aws/) |
| **Azure** | Terraform (Container Apps + Key Vault) | [`infra/terraform/azure/`](infra/terraform/azure/) |

---

## ⚡ Inicio Rápido (Docker Local)

### 1. Clonar y configurar variables de entorno
```bash
git clone https://github.com/DnRT/GMA-DEV.git
cd GMA-DEV
cp .env.example .env
```

Edita `.env` con tus tokens de Discord, Telegram, WhatsApp y Clarity.

### 2. Levantar con Docker Compose
```bash
docker compose up -d --build
```

El servicio iniciará los monitores programados y expondrá la API de webhooks en `http://localhost:8080`.

---

## 🧩 Plugins & Extensibilidad con Inteligencia Artificial

GMA-DEV incluye un plugin modular de enriquecimiento con IA (`AIEnricherPlugin`):
* **Ollama (100% Local y Offline):** Analiza logs y anomalías sin enviar datos fuera de tu red privada.
* **Google Gemini / OpenAI:** Opcional para generar resúmenes ejecutivos matutinos del estado de salud web.

---

## 📜 Licencia y Seguridad
* Licencia: [MIT](LICENSE)
* Políticas de seguridad y cumplimiento legal: [SECURITY.md](SECURITY.md)
