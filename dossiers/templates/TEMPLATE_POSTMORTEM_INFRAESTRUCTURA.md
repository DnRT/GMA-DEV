# INFORME POST-MORTEM DE INCIDENTE & ANÁLISIS DE CAUSA RAÍZ (RCA)
## REPORTE DE DISPONIBILIDAD OPERATIVA Y CUMPLIMIENTO DE SLA

---

**ID DE INCIDENTE:** `[INC-CRASH-YYYYMMDD-ID]`  
**SERVICIO AFECTADO:** `[Nombre del Servicio o Microservicio]`  
**SEVERIDAD:** `[CRÍTICO / ALTO]`  
**AUTOR DEL INFORME:** `[Nombre del Ingeniero DevOps]`  
**ESTADO:** `[RESUELTO / MITIGADO]`  

---

## 1. RESUMEN EJECUTIVO
`[Breve párrafo describiendo qué ocurrió, cuándo ocurrió, cómo se detectó y cómo se solucionó.]`

---

## 2. MÉTRICAS CLAVE DE IMPACTO (SLAs)

| Métrica Operativa | Valor Registrado | Meta / Compromiso SLA |
| :--- | :--- | :--- |
| **Tiempo de Detección (MTTD):** | `[X minutos / segundos]` | `< 1 minuto` |
| **Tiempo de Reconocimiento (MTTA):** | `[X minutos]` | `< 5 minutos` |
| **Tiempo Medio de Recuperación (MTTR):** | `[X minutos]` | `< 15 minutos` |
| **Disponibilidad Mensual Afectada:** | `[XX.XX%]` | `≥ 99.95%` |
| **Usuarios / Transacciones Afectadas:** | `[X usuarios / órdenes]` | `0 críticas` |

---

## 3. CRONOLOGÍA DE LOS HECHOS (TIMELINE)

* **[HH:MM UTC]:** `[Evento 1: Comienzo de la anomalía o pico de carga]`
* **[HH:MM UTC]:** `[Evento 2: Primer fallo HTTP 5xx registrado]`
* **[HH:MM UTC]:** `[Evento 3: Notificación de GMA-DEV recibida en Discord/Telegram]`
* **[HH:MM UTC]:** `[Evento 4: Diagnóstico y aplicación de parche / reinicio]`
* **[HH:MM UTC]:** `[Evento 5: Recuperación y emisión de alerta RESOLVED]`

---

## 4. ANÁLISIS DE CAUSA RAÍZ (LOS 5 PORQUÉS)

1. **¿Por qué falló el servicio?** `[Respuesta]`
2. **¿Por qué?** `[Respuesta]`
3. **¿Por qué?** `[Respuesta]`
4. **¿Por qué?** `[Respuesta]`
5. **Causa Raíz Definitiva:** `[Conclusión técnica]`

---

## 5. PLAN DE ACCIÓN Y MEDIDAS PREVENTIVAS

| Acción Correctiva | Responsable | Fecha Límite | Estado |
| :--- | :--- | :--- | :--- |
| `[Acción 1: Parche o configuración]` | `[Ingeniero]` | `[Fecha]` | `[Pendiente / Hecho]` |
| `[Acción 2: Mejora de monitoreo en GMA-DEV]` | `[DevOps]` | `[Fecha]` | `[Pendiente]` |
