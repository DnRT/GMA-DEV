# Guía de Telemetría: Microsoft Clarity & Healthchecks Proactivos

**GMA-DEV** combina dos niveles de observabilidad:
1. **Telemetría de Experiencia de Usuario (Frontend / UX):** Mediante la API de Microsoft Clarity.
2. **Telemetría de Infraestructura (Backend / Red):** Mediante healthchecks periódicos de endpoints HTTP/HTTPS y webhooks entrantes.

---

## 1. Integración con Microsoft Clarity API

Microsoft Clarity es una herramienta gratuita de analítica de comportamiento. GMA-DEV consulta periódicamente su API para detectar degradación silenciosa del servicio que las herramientas de infraestructura no logran ver.

### ¿Qué métricas monitorea GMA-DEV?

| Métrica | Significado Técnico | Umbral por Defecto |
| :--- | :--- | :--- |
| **Rage Clicks** | El usuario hace clic repetidamente de forma rápida en el mismo elemento. Indica botones colgados, peticiones API lentas o JavaScript bloqueado. | > 25 clics en ventana de muestreo |
| **Dead Clicks** | El usuario hace clic en un elemento interactivo que no produce ninguna respuesta. Indica enlaces rotos o handlers fallidos. | Monitoreado en reporte diario |
| **JavaScript Errors** | Excepciones no controladas en el navegador del cliente (ej. fallo al cargar un SDK de pago o error de parseo JSON). | > 20 errores en ventana de muestreo |
| **Active Users / Sessions** | Volumen de tráfico en vivo para contextualizar el porcentaje de error. | Telemetría base |

---

### Paso a paso para obtener las credenciales de Clarity

#### Paso 1: Localizar tu `Project ID`
1. Ingresa a tu panel de [Microsoft Clarity](https://clarity.ms/).
2. Selecciona tu proyecto.
3. Observa la URL en tu navegador; tiene la siguiente forma:
   ```text
   https://clarity.ms/projects/view/abcdef1234/dashboard
   ```
   El fragmento `abcdef1234` es tu **Project ID**.

#### Paso 2: Generar el `API Token`
1. En el panel de Clarity, haz clic en el icono de **Configuración (Settings)** en la esquina superior derecha.
2. En el menú izquierdo, busca la sección **Data Export** (o **API / Integrations**).
3. Haz clic en **Generate API Token** (o Export Token).
4. Copia el token alfanumérico generado.

#### Paso 3: Configurar en `.env`
```dotenv
CLARITY_ENABLED=true
CLARITY_API_TOKEN=tu-clarity-api-token-aqui
CLARITY_PROJECT_ID=abcdef1234
CLARITY_CHECK_INTERVAL_MINUTES=60
```

---

## 2. Monitoreo Proactivo de Endpoints (Healthchecks)

GMA-DEV ejecuta verificaciones periódicas (`GET` o `HEAD`) contra tus servicios y APIs para medir disponibilidad y latencia sin ser invasivo (cumpliendo la Ley 21.459).

### Formato de Configuración en `MONITORED_TARGETS`

La variable `MONITORED_TARGETS` recibe un arreglo JSON con los endpoints a vigilar:

```dotenv
MONITORED_TARGETS='[
  {
    "name": "API Gateway Principal",
    "url": "https://api.tuempresa.cl/healthz",
    "interval_seconds": 60,
    "expected_status": 200,
    "timeout_seconds": 5.0
  },
  {
    "name": "Portal Clientes",
    "url": "https://app.tuempresa.cl/",
    "interval_seconds": 120,
    "expected_status": 200,
    "timeout_seconds": 10.0
  }
]'
```

### Transiciones de Estado Automáticas
* **Transición `UP -> DOWN`:** Cuando un endpoint falla (status distinto al esperado, timeout o fallo DNS), GMA-DEV genera un incidente **CRITICAL** inmediato y notifica a los canales configurados.
* **Transición `DOWN -> UP`:** Cuando el servicio vuelve a responder con el código esperado, GMA-DEV emite una alerta **RESOLVED** verde indicando el restablecimiento del servicio y la nueva latencia.

---

## 3. Webhooks Entrantes (Grafana, Alertmanager, Sentry, Uptime Kuma)

Si ya tienes herramientas de monitoreo existentes en tu infraestructura, puedes enviar incidentes directamente al endpoint de ingesta de GMA-DEV:

### Endpoint:
`POST http://<tu-host>:8080/api/v1/webhook/incident`

### Payload JSON de ejemplo:
```json
{
  "id": "inc-db-9082",
  "service_name": "PostgreSQL Cluster",
  "severity": "CRITICAL",
  "title": "Conexiones agotadas en la base de datos",
  "description": "El pool de conexiones superó el 95% de capacidad. Se rechazan nuevas transacciones para el usuario 18.234.567-8 con token eyJhbGciOi...",
  "status_code": 503,
  "endpoint": "db.interno:5432"
}
```

> [!NOTE]
> Nota que el payload de ejemplo contiene un RUT y un token. GMA-DEV pasará automáticamente el mensaje por el **Pipeline de Sanitización** antes de despacharlo a Discord, Telegram o WhatsApp, asegurando que ninguna credencial o dato personal sea expuesto.
