# Despliegue en Amazon Web Services (AWS) con Terraform

Esta guía describe cómo desplegar **GMA-DEV** en AWS utilizando contenedores sin servidor con **Amazon ECS Fargate** y **AWS Secrets Manager**.

---

## 1. Arquitectura en AWS

* **Amazon ECS (Fargate):** Ejecuta el contenedor de GMA-DEV de forma serverless sin necesidad de administrar servidores EC2.
* **AWS Secrets Manager:** Guarda de forma segura los webhooks y tokens de notificación, inyectándolos como variables de entorno directamente en la definición de la tarea de ECS.
* **Amazon ECR (Elastic Container Registry):** Almacena las imágenes Docker de GMA-DEV.
* **IAM Roles de Mínimo Privilegio:** Un rol de ejecución (`ecs_execution_role`) con permisos estrictamente limitados a descargar la imagen y leer los secretos especificados.

---

## 2. Requisitos Previos

* **AWS CLI** instalado y configurado con credenciales (`aws configure`).
* **Terraform** instalado (`>= 1.5.0`).
* Permisos de administrador o rol con capacidad para crear recursos ECS, IAM y Secrets Manager.

---

## 3. Paso a Paso

### Paso 1: Crear el repositorio ECR y subir la imagen
```bash
# 1. Crear repositorio en tu región (ej. us-east-1)
aws ecr create-repository --repository-name gma-dev --region us-east-1

# 2. Autenticar Docker con ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin TU_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# 3. Construir y subir imagen
docker build -t TU_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/gma-dev:latest .
docker push TU_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/gma-dev:latest
```

---

### Paso 2: Configurar y Desplegar con Terraform
Navega a la carpeta de infraestructura de AWS:
```bash
cd infra/terraform/aws
```

Crea tu archivo `terraform.tfvars`:
```hcl
aws_region       = "us-east-1"
container_image  = "TU_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/gma-dev:latest"
telegram_chat_id = "987654321"
```

Aplica la configuración:
```bash
terraform init
terraform plan
terraform apply
```

---

### Paso 3: Cargar los Valores en Secrets Manager
Una vez creados los recursos, asigna el valor a los secretos en AWS:

```bash
# Guardar Webhook de Discord
aws secretsmanager put-secret-value \
  --secret-id ops-sentinel/discord-webhook \
  --secret-string "https://discord.com/api/webhooks/TU_DISCORD_WEBHOOK" \
  --region us-east-1

# Guardar Token de Telegram
aws secretsmanager put-secret-value \
  --secret-id ops-sentinel/telegram-token \
  --secret-string "7123456789:ABCdefGhIJKlmNoPQRstuVWXyz" \
  --region us-east-1
```

---

## 4. Alternativa Ultra-Rápida: AWS App Runner

Si prefieres no configurar VPCs y subredes para ECS Fargate, puedes desplegar la misma imagen en **AWS App Runner** directamente desde la consola de AWS o con CLI:
1. Ve a **AWS App Runner** -> **Create service**.
2. Origen: **Container registry** -> Selecciona tu imagen de ECR.
3. Puerto: `8080`.
4. Variables de entorno: Vincula los secretos desde Secrets Manager.
5. App Runner te proporcionará una URL HTTPS pública de alta disponibilidad en menos de 3 minutos.
