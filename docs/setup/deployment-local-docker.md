# Despliegue Local con Docker & Docker Compose

Esta guía cubre la puesta en marcha local de **GMA-DEV**, ya sea para desarrollo, pruebas internas o despliegue en un servidor bare-metal / VPS propio.

---

## 1. Requisitos Previos

* **Docker Engine** (versión 24.0+ recomendada)
* **Docker Compose** (v2 o superior)
* Git instalado

---

## 2. Estructura de Seguridad del Contenedor

El [`Dockerfile`](../../Dockerfile) oficial implementa un empaquetado multi-etapa (*multi-stage build*) con las siguientes garantías:
* **Usuario sin privilegios (`appuser`, UID 10001):** Nunca corre como `root`, previniendo escalada de privilegios en el host (cumple Ley 21.663 y CIS Benchmark).
* **Volumen persistente para auditoría:** Los logs de auditoría inmutables se escriben en `/app/audit_logs/incidents.jsonl` y se montan en el host para persistencia a largo plazo.
* **Healthcheck nativo integrado:** Verifica periódicamente el endpoint `/healthz`.

---

## 3. Puesta en Marcha Básica

### Paso 1: Configurar variables de entorno
```bash
cp .env.example .env
```
Abre `.env` en tu editor preferido y ajusta al menos un canal de salida:
```dotenv
DISCORD_ENABLED=true
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### Paso 2: Construir e iniciar el contenedor
```bash
docker compose up -d --build
```

### Paso 3: Verificar estado y salud
Verifica que el contenedor esté corriendo y saludable:
```bash
docker compose ps
```
Deberías ver:
```text
NAME         IMAGE              COMMAND                  SERVICE      STATUS
gma-dev      gma-dev:latest     "python -m src.main"     gma-dev      Up (healthy)
```

Prueba el endpoint de salud desde tu terminal:
```bash
curl http://localhost:8080/healthz
```
Respuesta esperada:
```json
{
  "status": "healthy",
  "timestamp": "2026-10-30T19:50:00.000000Z",
  "active_channels": ["discord"],
  "ley_21663_compliance": true
}
```

---

## 4. Despliegue con Inteligencia Artificial Local (Ollama)

GMA-DEV incluye un perfil en `docker-compose.yml` que levanta una instancia local de **Ollama** en la misma red privada de Docker, permitiendo diagnósticos con IA **completamente offline y sin enviar datos fuera de tu máquina**.

### Paso 1: Iniciar con el perfil `ai`
```bash
docker compose --profile ai up -d --build
```

### Paso 2: Descargar el modelo en Ollama
Una vez iniciado el contenedor de Ollama, descarga el modelo ligero recomendado (`llama3.2`):
```bash
docker exec -it gma-dev-ollama ollama pull llama3.2
```

### Paso 3: Activar en tu archivo `.env`
```dotenv
AI_ENRICHER_ENABLED=true
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2
```

Reinicia el contenedor principal para aplicar cambios:
```bash
docker compose restart gma-dev
```

A partir de este momento, cada incidente detectado incluirá un análisis conciso de causa raíz sugerido por el modelo local.

---

## 5. Inspección de Auditoría Local (Ley 21.663)

Los eventos e incidentes detectados se guardan en la carpeta `./audit_logs/incidents.jsonl` de tu host. Puedes inspeccionarlos en tiempo real:

```bash
tail -f audit_logs/incidents.jsonl
```

Cada línea incluye la marca temporal UTC, los detalles técnicos del fallo y su firma SHA-256 de verificación.
