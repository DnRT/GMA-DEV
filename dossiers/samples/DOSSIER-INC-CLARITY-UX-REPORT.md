# EXPEDIENTE DE INVESTIGACIÓN UX & FRICCIÓN EN CLIENTE
## ANÁLISIS DE TELEMETRÍA DE COMPORTAMIENTO Y ERRORES FRONTEND (MICROSOFT CLARITY)

---

**ID DE INCIDENTE:** `INC-CLARITY-1793394442`  
**PROYECTO CLARITY:** `w13cujuo4o`  
**SEVERIDAD:** `WARNING (DEGRADACIÓN DE EXPERIENCIA)`  
**SISTEMA AFECTADO:** `Página de Carro de Compras y Checkout (/carro-compras)`  
**ESTADO:** `INVESTIGACIÓN COMPLETADA / PARCHE EN REVISIÓN`  

---

## 1. RESUMEN DE LA ANOMALÍA UX

El motor **GMA-DEV** detectó un pico anormal de frustración de usuarios en el portal de comercio electrónico: **42 Rage Clicks (clics de rabia/frustración)** y **18 Dead Clicks (clics en elementos no interactivos)** dentro de una ventana de muestreo de 5 minutos, afectando a más de 150 usuarios concurrentes.

A pesar de que el servidor backend respondía **HTTP 200 OK**, la interfaz de usuario se congelaba silenciosamente en dispositivos móviles Android al presionar el botón de selección de medio de pago.

---

## 2. MÉTRICAS DE COMPORTAMIENTO DETECTADAS (CLARITY METRICS)

| Métrica de Fricción | Valor Registrado | Línea Base Normal | Desviación |
| :--- | :--- | :--- | :--- |
| **Rage Clicks:** | `42 clics` | `< 5 clics / 10m` | `+740% (Crítico)` |
| **Dead Clicks:** | `18 clics` | `< 3 clics / 10m` | `+500% (Anormal)` |
| **Errores de Script JS:** | `26 excepciones` | `0 errores` | `Requiere Parche` |
| **Scroll Rápido Excesivo:** | `14 sesiones` | `< 2 sesiones` | Desesperación de usuario |
| **Sesiones Afectadas:** | `38 usuarios únicos` | `0` | Pérdida de conversión |

---

## 3. SESIONES CLAVE GRABADAS (EVIDENCIA AUDIOVISUAL)

> Mediante la integración de GMA-DEV con la API de Clarity, los siguientes enlaces permiten reproducir exactamente lo que vio el usuario antes de abandonar la compra:

* **Grabación de Sesión #1 (Fallo en Móvil Chrome):**  
  [https://clarity.ms/projects/view/w13cujuo4o/impressions/session-rec-001](https://clarity.ms/projects/view/w13cujuo4o/dashboard)
* **Grabación de Sesión #2 (Clics repetidos en botón de pago):**  
  [https://clarity.ms/projects/view/w13cujuo4o/impressions/session-rec-002](https://clarity.ms/projects/view/w13cujuo4o/dashboard)

---

## 4. ANÁLISIS DE LA EXCEPCIÓN JAVASCRIPT (CLIENT-SIDE ERROR)

El log de Clarity capturó la siguiente excepción no controlada en el navegador de los clientes:

```javascript
Uncaught TypeError: Cannot read properties of undefined (reading 'initTransbankSDK')
    at HTMLButtonElement.<anonymous> (checkout.bundle.js:142:18)
    at HTMLButtonElement.dispatch (vendor.js:8920:9)
    at v.handle (vendor.js:8624:43)
```

### Diagnóstico Técnico:
1. El script del SDK de la pasarela de pagos se cargaba de forma asíncrona (`defer`) pero sin una promesa de resolución que garantizara su disponibilidad antes de que el usuario interactuara con el botón.
2. En conexiones 3G/4G con mayor latencia, el usuario hacía clic antes de que el objeto estuviera montado en `window.Transbank`, arrojando `TypeError`.
3. El botón permanecía habilitado visualmente pero sin respuesta interactiva, provocando que los usuarios hicieran entre 5 y 10 clics seguidos con frustración.

---

## 5. ACCIONES CORRECTIVAS APLICADAS

1. **Estado de Carga en Botón:** Modificar el botón de pago para que muestre un *spinner* de carga deshabilitado hasta que todos los SDKs externos confirmen el evento `window.onload`.
2. **Fallback y Manejador de Error:** Envolver la llamada al SDK en un bloque `try/catch` con reintento automático y mensaje amigable en pantalla: *"Cargando pasarela segura, por favor espere un segundo..."*.
3. **Métrica de Alerta en GMA-DEV:** Ajustar el umbral de notificación de Clarity en GMA-DEV a **15 rage clicks** para detectar estos problemas con menor latencia.
