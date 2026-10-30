# Guía de Configuración de Canales: Telegram, Discord y WhatsApp

Esta guía explica paso a paso cómo obtener las credenciales y configurar desde cero cada uno de los tres canales de notificación soportados por **GMA-DEV**.

---

## 1. Telegram Bot API (Recomendado para Alertas Móviles Inmediatas)

Telegram es el canal más sencillo, rápido y gratuito para recibir alertas en tiempo real con soporte para formato HTML.

### Paso 1: Crear el Bot con `@BotFather`
1. Abre tu aplicación de Telegram y busca el usuario oficial **`@BotFather`** (asegúrate de que tenga la insignia azul de verificación).
2. Inicia el chat y envía el comando:
   ```text
   /newbot
   ```
3. `@BotFather` te pedirá dos datos:
   * **Nombre visible:** El nombre que verás en el chat (ej. `GMA-DEV Alertas`).
   * **Username único:** Debe terminar en `bot` (ej. `gma_dev_ops_bot`).
4. Al crearse, `@BotFather` te entregará tu **HTTP API Token**, con un formato similar a:
   ```text
   7123456789:ABCdefGhIJKlmNoPQRstuVWXyz_1234567
   ```
   *Guarda este valor para la variable `TELEGRAM_BOT_TOKEN`.*

### Paso 2: Obtener tu `Chat ID` (Personal o Grupo)
Para que el bot sepa a dónde enviar los mensajes, necesitas tu identificador de chat:

* **Para chat personal:**
  1. Busca el bot **`@userinfobot`** en Telegram y pulsa `/start`.
  2. Te responderá con tu `Id` numérico (ej. `987654321`).
  3. **Importante:** Debes abrir un chat con tu bot recién creado y pulsar `/start` una vez para autorizarlo a enviarte mensajes.
* **Para un grupo de trabajo u operaciones:**
  1. Crea un grupo en Telegram y añade a tu bot como miembro (o administrador).
  2. Envía cualquier mensaje en el grupo (ej. `Hola bot`).
  3. Abre en tu navegador la siguiente URL reemplazando tu token:
     ```text
     https://api.telegram.org/bot<TU_TELEGRAM_BOT_TOKEN>/getUpdates
     ```
  4. Busca en el JSON el campo `"chat":{"id": -1001234567890}`. Los IDs de grupos o canales siempre comienzan con `-` o `-100`.

### Paso 3: Configurar en `.env`
```dotenv
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=7123456789:ABCdefGhIJKlmNoPQRstuVWXyz_1234567
TELEGRAM_CHAT_ID=987654321
```

---

## 2. Discord Webhooks (Recomendado para Visualización con Rich Embeds)

Discord permite enviar alertas estilizadas con barras de color dinámicas (rojo para caídas críticas, verde para recuperaciones).

### Paso 1: Crear el Webhook en tu Servidor de Discord
1. Abre tu servidor de Discord y entra a los **Ajustes del Servidor** (o del canal donde quieras las alertas, ej. `#ops-alertas`).
2. Ve a la pestaña **Integraciones** -> **Webhooks** -> haz clic en **Nuevo Webhook**.
3. Configura:
   * **Nombre:** `GMA-DEV AlertManager`
   * **Canal:** Selecciona el canal destino (ej. `#ops-alertas`).
   * *(Opcional)* Sube un avatar representativo.
4. Haz clic en **Copiar URL de Webhook**. La URL tendrá una estructura como:
   ```text
   https://discord.com/api/webhooks/123456789012345678/abcdefghijklmnopqrstuvwxyz0123456789_ABCDEF
   ```

### Paso 2: Configurar en `.env`
```dotenv
DISCORD_ENABLED=true
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789012345678/abcdefghijklmnopqrstuvwxyz0123456789_ABCDEF
```

---

## 3. WhatsApp (Meta Cloud API Oficial & Alternativa Twilio)

WhatsApp es el canal con mayor tasa de apertura para guardias o emergencias críticas. GMA-DEV soporta la **API oficial de Meta** (WhatsApp Cloud API) y una alternativa rápida mediante **Twilio**.

### Opción A: Meta Cloud API Oficial (Desde Cero)

#### Paso 1: Crear una cuenta en Meta for Developers
1. Ingresa a [developers.facebook.com](https://developers.facebook.com/) e inicia sesión con tu cuenta de Facebook.
2. Si es tu primera vez, completa el registro como desarrollador.

#### Paso 2: Crear una Aplicación Empresarial
1. En el panel superior, haz clic en **Mis apps** -> **Crear app**.
2. Selecciona el tipo de app: **Empresa (Business)** o **Otro -> Empresa** y pulsa Siguiente.
3. Asigna un nombre a la app (ej. `GMA-DEV Monitor`) y selecciona tu cuenta de Meta Business Manager (o crea una nueva).

#### Paso 3: Configurar el producto WhatsApp
1. En el panel de control de tu app, busca el cuadro de **WhatsApp** y pulsa **Configurar**.
2. Ve al menú lateral: **WhatsApp** -> **Inicio rápido** (o **Configuración de la API**).
3. Meta te proporcionará inmediatamente un entorno de pruebas con:
   * **Identificador de número de teléfono (Phone Number ID):** Un número de 15 dígitos (ej. `109876543210987`).
   * **Token de acceso temporal:** Válido por 24 horas para desarrollo inicial.
4. En la sección *"Para"*, agrega tu propio número de teléfono móvil real y verifica el código de 6 dígitos que te llegará por WhatsApp para autorizar el envío de pruebas.

#### Paso 4: Generar un Token Permanente (System User Token)
Para producción no puedes usar el token de 24 horas; debes crear un token permanente de usuario del sistema:
1. Ingresa al [Meta Business Manager](https://business.facebook.com/settings).
2. Ve a **Configuración del negocio** -> **Usuarios** -> **Usuarios del sistema**.
3. Haz clic en **Agregar**, nombra al usuario (ej. `gma-dev-service`) y asígnale el rol de **Administrador**.
4. Haz clic en **Generar nuevo token**, selecciona tu app `GMA-DEV Monitor`.
5. En los permisos requeridos, marca obligatoriamente:
   * `whatsapp_business_messaging`
   * `whatsapp_business_management`
6. Copia el token generado permanente (comienza con `EAAG...`).

#### Paso 5: Crear una Plantilla de Mensaje (Message Template)
Meta exige que los mensajes proactivos (iniciados por el bot fuera de una conversación activa de 24h) usen plantillas aprobadas:
1. En el panel de WhatsApp, entra a **Plantillas de mensajes**.
2. Pulsa **Crear plantilla**:
   * Categoría: **Utilidad (Utility)**.
   * Nombre: `incident_alert_v1`.
   * Idioma: Español (`es`) o Inglés (`en_US`).
   * Cuerpo del texto:
     ```text
     [GMA-DEV] Alerta {{1}}: El servicio {{2}} ha fallado con estado {{3}}. ID: {{4}}
     ```
3. Envía la plantilla a revisión (generalmente se aprueba en 1 a 15 minutos).

#### Paso 6: Configurar en `.env`
```dotenv
WHATSAPP_ENABLED=true
WHATSAPP_PROVIDER=meta
WHATSAPP_PHONE_NUMBER_ID=109876543210987
WHATSAPP_ACCESS_TOKEN=EAAG...tu-token-permanente...
WHATSAPP_RECIPIENT_PHONE=+56912345678
WHATSAPP_TEMPLATE_NAME=incident_alert_v1
```

---

### Opción B: Alternativa rápida con Twilio WhatsApp Sandbox

Si no deseas pasar por el proceso de verificación de Meta Business, puedes usar el Sandbox de Twilio en minutos:

1. Crea una cuenta en [Twilio](https://www.twilio.com/).
2. Ve a **Messaging** -> **Try it out** -> **Send a WhatsApp message**.
3. Sigue las instrucciones para unirte al Sandbox (enviar un mensaje de WhatsApp desde tu teléfono con una palabra clave como `join simple-word` al número de Twilio).
4. Copia desde el panel principal de Twilio:
   * **Account SID**
   * **Auth Token**
   * **WhatsApp From Number** (ej. `+14155238886`)
5. Configura en `.env`:
   ```dotenv
   WHATSAPP_ENABLED=true
   WHATSAPP_PROVIDER=twilio
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=tu_auth_token_de_twilio
   TWILIO_WHATSAPP_FROM=+14155238886
   WHATSAPP_RECIPIENT_PHONE=+56912345678
   ```
