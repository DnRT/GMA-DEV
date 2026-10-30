# Despliegue en Microsoft Azure con Terraform

Esta guía cubre el despliegue de **GMA-DEV** en **Microsoft Azure** utilizando **Azure Container Apps (ACA)** y un entorno administrado con **Log Analytics**.

---

## 1. Arquitectura en Azure

* **Azure Container Apps:** Servicio de contenedores serverless basado en Kubernetes (KEDA), ideal para microservicios y bots con escalado eficiente.
* **Log Analytics Workspace:** Centralización de logs de contenedor con retención configurable.
* **Azure Container Registry (ACR):** Repositorio privado para hospedar la imagen Docker.

---

## 2. Requisitos Previos

* **Azure CLI (`az`)** instalado y autenticado:
  ```bash
  az login
  ```
* **Terraform** instalado (`>= 1.5.0`).
* Una suscripción activa de Azure.

---

## 3. Paso a Paso

### Paso 1: Crear ACR y subir la imagen Docker
```bash
# 1. Crear Resource Group y ACR (ej. en región brazilsouth o eastus)
az group create --name rg-gma-dev --location brazilsouth
az acr create --resource-group rg-gma-dev --name gmadevacr --sku Basic --admin-enabled true

# 2. Iniciar sesión en ACR
az acr login --name gmadevacr

# 3. Construir y subir imagen
docker build -t gmadevacr.azurecr.io/gma-dev:latest .
docker push gmadevacr.azurecr.io/gma-dev:latest
```

---

### Paso 2: Desplegar con Terraform
Navega a la carpeta de infraestructura de Azure:
```bash
cd infra/terraform/azure
```

Crea tu archivo `terraform.tfvars`:
```hcl
resource_group_name = "rg-gma-dev"
location            = "brazilsouth"
container_image     = "gmadevacr.azurecr.io/gma-dev:latest"
telegram_chat_id    = "987654321"
```

Aplica la configuración:
```bash
terraform init
terraform plan
terraform apply
```

Al terminar, Azure Container Apps te proporcionará un FQDN público con certificado SSL automático (ej. `https://ops-sentinel-app.brazilsouth.azurecontainerapps.io`).

---

## 4. Estrategia de Resiliencia Multi-Cloud (GCP + Azure / Local)

Para evitar que una falla global de un proveedor de nube o problemas de enrutamiento/DNS en Cloudflare dejen a tu equipo a ciegas:

1. **Instancia Primaria en Cloud (GCP o Azure):** Monitorea continuamente las APIs y servicios públicos desde la nube.
2. **Instancia Secundaria en Local / On-Premise (Docker Compose):** Corre en un servidor local o VPS independiente. Si la nube o el proveedor de DNS tiene interferencias, la instancia local sigue alertando a través de rutas de red distintas hacia Telegram y Discord.
3. **Idempotencia de Alertas:** Al utilizar el ID único de cada incidente (`id`), las alertas no se duplican indebidamente en los canales.
