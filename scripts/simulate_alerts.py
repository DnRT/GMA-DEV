import time
import argparse
import httpx

BASE_URL = "http://localhost:8080"


def send_incident(payload: dict, label: str):
    print(f"\n[SIMULACION] Disparando: {label}...")
    try:
        res = httpx.post(f"{BASE_URL}/api/v1/webhook/incident", json=payload, timeout=10.0)
        if res.status_code == 200:
            print(f"  [OK] Incidente '{payload['id']}' aceptado por el motor central.")
            print(f"  -> Revisa tu canal de Discord para ver el formato y las mascaras aplicadas.")
        else:
            print(f"  [ERROR] Status HTTP {res.status_code}: {res.text}")
    except Exception as e:
        print(f"  [ERROR] No se pudo conectar a GMA-DEV en {BASE_URL}: {e}")


def scenario_crash():
    payload = {
        "id": f"INC-CRASH-{int(time.time())}",
        "service_name": "API Checkout & Pagos",
        "severity": "CRITICAL",
        "title": "Fallo Critico: HTTP 502 Bad Gateway",
        "description": "El proxy inverso upstream no respondio tras 10.000 ms. El servicio de pagos esta inaccesible para los clientes.",
        "status_code": 502,
        "response_time_ms": 10042.8,
        "endpoint": "https://api.tuempresa.cl/v1/checkout/transbank"
    }
    send_incident(payload, "1. Caida de Servicio (HTTP 502 / Critical)")


def scenario_recovery():
    payload = {
        "id": f"INC-RECOV-{int(time.time())}",
        "service_name": "API Checkout & Pagos",
        "severity": "RESOLVED",
        "title": "Servicio Restablecido: API Checkout OK",
        "description": "El contenedor backend reinicio exitosamente. Los healthchecks responden HTTP 200 con latencia normal.",
        "status_code": 200,
        "response_time_ms": 48.2,
        "endpoint": "https://api.tuempresa.cl/v1/checkout/transbank"
    }
    send_incident(payload, "2. Recuperacion de Servicio (Resolved / Green)")


def scenario_security():
    payload = {
        "id": f"INC-SEC-{int(time.time())}",
        "service_name": "WAF & Auth Gateway",
        "severity": "CRITICAL",
        "title": "Intento de Intrusion: SQL Injection detectado",
        "description": "Intento de bypass de autenticacion para usuario con RUT 19.876.543-k mediante inyeccion en parametro 'token' con Bearer eyJhbGciOi...",
        "status_code": 403,
        "response_time_ms": 15.1,
        "endpoint": "https://api.tuempresa.cl/auth/login",
        "evidence": {
            "source_ip": "185.220.101.5",
            "attack_vector": "SQL Injection / Auth Bypass",
            "raw_payload_snippet": "admin' OR 1=1 --",
            "clarity_session_url": "https://clarity.ms/projects/view/w13cujuo4o/impressions/demo-attack-session"
        }
    }
    send_incident(payload, "3. Incidente de Ciberseguridad (IP enmascarada + Boveda ANCI Ley 21.663)")


def scenario_clarity_ux():
    payload = {
        "id": f"INC-CLARITY-{int(time.time())}",
        "service_name": "Frontend UX (Microsoft Clarity)",
        "severity": "WARNING",
        "title": "Pico de Rage Clicks: Boton de Checkout Bloqueado",
        "description": "Microsoft Clarity detecto 42 clics de frustracion y 18 clics muertos en la pagina /carro-compras en los ultimos 5 minutos.",
        "status_code": 200,
        "endpoint": "https://tuempresa.cl/carro-compras",
        "evidence": {
            "attack_vector": "Frontend UX Friction / Unresponsive UI",
            "clarity_session_url": "https://clarity.ms/projects/view/w13cujuo4o/dashboard"
        },
        "metadata": {
            "rage_clicks": 42,
            "dead_clicks": 18,
            "active_users": 156
        }
    }
    send_incident(payload, "4. Frustracion de Usuario en Frontend (Microsoft Clarity)")


def scenario_report():
    print("\n[SIMULACION] Disparando: 5. Reporte Consolidado de Salud...")
    try:
        res = httpx.post(f"{BASE_URL}/api/v1/report/trigger", timeout=10.0)
        if res.status_code == 200:
            print("  [OK] Reporte solicitado. GMA-DEV consulto Clarity y genero el informe consolidado.")
            print("  -> Revisa tu canal de Discord para ver el resumen ejecutivo.")
        else:
            print(f"  [ERROR] Status HTTP {res.status_code}: {res.text}")
    except Exception as e:
        print(f"  [ERROR] No se pudo conectar a GMA-DEV: {e}")


def main():
    parser = argparse.ArgumentParser(description="Simulador de Alertas para GMA-DEV")
    parser.add_argument(
        "--scenario",
        choices=["crash", "recovery", "security", "clarity", "report", "all"],
        default="all",
        help="Escenario a simular (default: all)"
    )
    args = parser.parse_args()

    scenarios = {
        "crash": scenario_crash,
        "recovery": scenario_recovery,
        "security": scenario_security,
        "clarity": scenario_clarity_ux,
        "report": scenario_report
    }

    if args.scenario == "all":
        print("=== Iniciando Simulacion Completa de los 5 Escenarios en GMA-DEV ===")
        for name, fn in scenarios.items():
            fn()
            time.sleep(2)
        print("\n[EXITO] Todos los escenarios fueron enviados. Abre tu Discord para ver los resultados en vivo!")
    else:
        scenarios[args.scenario]()


if __name__ == "__main__":
    main()
