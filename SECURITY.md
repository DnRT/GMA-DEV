# Security & Legal Compliance Policy

## 1. Alcance Normativo y Legal (Chile & Internacional)

GMA-DEV (*Get My Alert, Developer*) ha sido concebido desde su concepción (*Security and Privacy by Design*) bajo los estándares de la legislación chilena y las directivas internacionales de protección de datos e infraestructura crítica.

### A. Ley Marco de Ciberseguridad de Chile (Ley Nº 21.663)
1. **Seguridad por Defecto y por Diseño (Art. 3):**
   - El contenedor oficial se ejecuta bajo un usuario sin privilegios (`appuser`, UID 10001).
   - Ninguna credencial, token o clave privada se almacena en código ni en imágenes de contenedores.
   - Las variables sensibles se inyectan en tiempo de ejecución mediante proveedores de secretos (GCP Secret Manager, AWS Secrets Manager, Azure Key Vault).
2. **Registro de Auditoría e Incidentes:**
   - Todo incidente detectado o notificado genera una traza JSON local inmutable con marcas temporales UTC en formato ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`).
   - Estos registros cumplen con los requerimientos de evidencia exigibles por la Agencia Nacional de Ciberseguridad (ANCI) y el CSIRT Nacional.

### B. Ley sobre Delitos Informáticos de Chile (Ley Nº 21.459 / Convenio de Budapest)
1. **Acceso Legítimo (Art. 2) e Interceptación (Art. 3):**
   - GMA-DEV no realiza escaneo de puertos intrusivo, ataques de denegación de servicio (DoS) ni interceptación no autorizada de paquetes.
   - Toda telemetría se realiza exclusivamente mediante consultas a endpoints públicos o autorizados de monitoreo (`/healthz`, `/metrics`, APIs con autenticación).
2. **Descargo de Responsabilidad (*Disclaimer*):**
   - El uso de esta herramienta está autorizado exclusivamente para la administración, monitoreo y diagnóstico de infraestructuras propias o bajo autorización contractual expresa. El operador del software asume la responsabilidad legal de los endpoints configurados.

### C. Protección de Datos Personales (Nueva Ley de Datos Personales / Ley 19.628 / GDPR)
1. **Principio de Minimización y Confidencialidad:**
   - La herramienta cuenta con un **Pipeline de Sanitización Mandatorio** que intercepta cualquier mensaje antes de su transmisión a canales externos (Discord, Telegram, WhatsApp).
   - Enmascara patrones de:
     - RUT chileno: `\b\d{1,2}\.?\d{3}\.?\d{3}-?[\dkK]\b` -> `[RUT_PROTEGIDO]`
     - Emails personales -> `[EMAIL_PROTEGIDO]`
     - Direcciones IP v4 / v6 de clientes -> `[IP_PUBLICA_PROTEGIDA]`
     - Tokens JWT, Bearer, Secret Keys y Passwords -> `[TOKEN_OCULTO]`
2. **Transferencia Internacional de Datos:**
   - Dado que los servidores de Discord, Telegram y Meta se encuentran fuera de la jurisdicción nacional, **está estrictamente prohibido y bloqueado a nivel de código el envío de volcados de bases de datos o información personal identifiable (PII)** a estos canales. Las alertas se emiten bajo el principio de "Punteros Técnicos Abstractos".

---

## 2. Reporte Responsable de Vulnerabilidades

Si descubres una vulnerabilidad de seguridad en GMA-DEV, por favor envía un reporte a través de los canales privados del repositorio o al correo del mantenedor. **No abras un Issue público para reportar fallos de seguridad.**

---

## 3. Prácticas Técnicas Obligatorias

* **Cifrado en Tránsito:** Conexiones salientes forzadas a HTTPS con TLS 1.3 / TLS 1.2.
* **Cero Confianza en Webhooks Entrantes:** Validación de firmas HMAC SHA-256 para eventos de Microsoft Clarity y fuentes externas.
* **Aislamiento de Plugins:** Los plugins de IA (Ollama, OpenAI, Gemini) solo reciben payloads previamente sanitizados por el motor central.
