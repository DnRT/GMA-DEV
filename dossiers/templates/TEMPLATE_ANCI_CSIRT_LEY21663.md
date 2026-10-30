# EXPEDIENTE DE NOTIFICACIÓN DE INCIDENTE DE CIBERSEGURIDAD
## FORMULARIO OFICIAL CSIRT NACIONAL / AGENCIA NACIONAL DE CIBERSEGURIDAD (ANCI)
### Conforme a las obligaciones de la Ley Marco de Ciberseguridad (Ley Nº 21.663 - Chile)

---

**ESTADO DEL EXPEDIENTE:** `[NOTIFICACIÓN PRELIMINAR (3 HORAS) / NOTIFICACIÓN COMPLETA (72 HORAS)]`  
**CÓDIGO DE INCIDENTE GMA-DEV:** `[INC-SEC-AÑO-NUMERO]`  
**NIVEL DE SEVERIDAD:** `[CRÍTICO / ALTO / MEDIO]`  
**FECHA Y HORA DE EMISIÓN:** `[YYYY-MM-DD HH:MM:SS UTC]` (`[HH:MM:SS CLT]`)  

---

## 1. IDENTIFICACIÓN DE LA ORGANIZACIÓN Y RESPONSABLE TÉCNICO

| Campo | Detalle Declarado |
| :--- | :--- |
| **Nombre de la Entidad / Operador:** | `[Razón Social de la Empresa]` |
| **RUT de la Entidad:** | `[XX.XXX.XXX-X]` |
| **Sector / Tipo de Entidad:** | `[Operador de Importancia Vital (OIV) / Servicio Esencial]` |
| **Responsable de Ciberseguridad / Notificante:** | `[Nombre y Cargo del Ingeniero/CISO]` |
| **Correo Electrónico de Contacto:** | `[seguridad@tuempresa.cl]` |
| **Teléfono de Emergencia 24/7:** | `[+56 9 XXXX XXXX]` |

---

## 2. CLASIFICACIÓN Y TAXONOMÍA DEL INCIDENTE (TAXONOMÍA CSIRT)

* **Categoría Principal:** `[Acceso No Autorizado / Intrusión / DoS / Código Malicioso]`
* **Subcategoría:** `[SQL Injection / XSS / Credential Stuffing / Ransomware]`
* **Vector de Ataque:** `[Descripción breve del vector de entrada]`
* **Impacto Operacional:** `[Crítico / Alto / Medio / Bajo]`
* **Impacto en Información:** `[Confidencialidad / Integridad / Disponibilidad / Datos Personales]`

---

## 3. LÍNEA DE TIEMPO FORENSE (TIMELINE)

| Marca Temporal (UTC) | Hora Local Chile (CLT) | Hito / Evento Forense |
| :--- | :--- | :--- |
| `[YYYY-MM-DD HH:MM:SSZ]` | `[HH:MM CLT]` | Detección inicial por WAF / Monitoreo GMA-DEV. |
| `[YYYY-MM-DD HH:MM:SSZ]` | `[HH:MM CLT]` | Disparo de alerta y reconocimiento por equipo de guardia. |
| `[YYYY-MM-DD HH:MM:SSZ]` | `[HH:MM CLT]` | Aplicación de medidas de contención perimetral. |
| `[YYYY-MM-DD HH:MM:SSZ]` | `[HH:MM CLT]` | Cierre de brecha o restauración del servicio. |

---

## 4. EVIDENCIA TÉCNICA E INDICADORES DE COMPROMISO (IOCs)

### A. Datos del Atacante
* **Dirección IP de Origen:** `[IP_ORIGEN_ATACANTE]`
* **País / ASN / Proveedor:** `[País / Proveedor / VPN / Tor]`
* **User-Agent / Herramienta:** `[User-Agent del atacante]`

### B. Activos Afectados
* **Endpoint / URL:** `[https://api.tuempresa.cl/...]`
* **Parámetro Afectado:** `[Parámetro o cabecera atacada]`
* **Fragmento de Payload:**
  ```text
  [Pegar aquí fragmento del ataque]
  ```

### C. Integridad y Validez Probatoria
* **Firma Criptográfica SHA-256 de Evidencia (Bóveda GMA-DEV):**
  `[HASH_SHA256_DE_AUDIT_LOGS]`
* **Grabación de Comportamiento (Microsoft Clarity / Logs):**
  `[https://clarity.ms/projects/view/.../dashboard]`

---

## 5. MEDIDAS DE MITIGACIÓN Y CONTENCIÓN ADOPTADAS

1. `[Medida inmediata 1: Bloqueo de IP en Firewall/WAF]`
2. `[Medida inmediata 2: Parche de código o rotación de credenciales]`
3. `[Medida inmediata 3: Revocación de sesiones o aislamiento de contenedor]`

---

## 6. DECLARACIÓN JURADA DE VERACIDAD

El presente informe ha sido preparado conforme a la **Ley Nº 21.663**, dejando constancia de que los registros expuestos son copias fieles de los sistemas de telemetría inmutables de la organización.

**Firma Responsable Técnico:**  
`[Nombre del Ingeniero]` — `[Cargo]`  
`[Empresa]`
