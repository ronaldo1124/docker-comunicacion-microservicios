# ==============================================================================
# Suite de Pruebas Automatizadas con Pytest - Entrega Proyecto 2
# Integración Continua y DevOps - Politécnico Grancolombiano
# ==============================================================================
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# Asegurar la correcta resolución de rutas para importar la aplicación Flask
APP_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = APP_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import main


@pytest.fixture
def client():
    """Configura el cliente de pruebas de Flask en modo TESTING."""
    main.app.config["TESTING"] = True
    with main.app.test_client() as client:
        yield client


# ==============================================================================
# 1. Pruebas de la Interfaz Web y Rutas Básicas
# ==============================================================================
def test_home_route(client):
    """Verifica que la página principal responda HTTP 200 y contenga la vista de la app."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Politécnico Grancolombiano" in html or "comunicación" in html.lower()


# ==============================================================================
# 2. Pruebas de Diagnóstico de Red y Requisitos de Comunicación
# ==============================================================================
def test_health_check_dns_and_service_name_success(client, monkeypatch):
    """
    Verifica que /api/health valide satisfactoriamente:
    - Uso del nombre de servicio 'db' (no localhost, no IP fija).
    - Resolución DNS mediante Docker Embedded DNS.
    - Conectividad exitosa simulada con PostgreSQL.
    """
    # Simular resolución DNS exitosa hacia la IP del contenedor db
    monkeypatch.setattr("socket.gethostbyname", lambda host: "172.28.0.2")

    # Mock de la conexión y cursor a PostgreSQL
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [
        {"version": "PostgreSQL 16.2 on x86_64-pc-linux-musl"},
        {"total": 5}
    ]
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    monkeypatch.setattr(main, "get_db_connection", lambda max_retries=2, delay=1: mock_conn)

    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["comunicacion_contenedor_destino"]["servicio_configurado"] == "db"
    assert data["comunicacion_contenedor_destino"]["ip_resuelta_por_dns"] == "172.28.0.2"
    assert data["comunicacion_contenedor_destino"]["conexion_establecida"] is True

    # Validaciones fundamentales de la rúbrica del proyecto
    requisitos = data["verificacion_requisitos"]
    assert requisitos["usa_nombre_servicio"] is True
    assert requisitos["no_usa_localhost"] is True
    assert requisitos["no_usa_ip_fija"] is True


def test_health_check_when_db_unreachable(client, monkeypatch):
    """Verifica que /api/health responda HTTP 503 (degraded) cuando la base de datos no está disponible."""
    monkeypatch.setattr("socket.gethostbyname", lambda host: "172.28.0.2")
    # Simular fallo en conexión a BD
    monkeypatch.setattr(main, "get_db_connection", lambda max_retries=2, delay=1: (_ for _ in ()).throw(Exception("DB connection timeout")))

    response = client.get("/api/health")
    assert response.status_code == 503

    data = response.get_json()
    assert data["status"] == "degraded"
    assert data["comunicacion_contenedor_destino"]["conexion_establecida"] is False
    requisitos = data["verificacion_requisitos"]
    assert requisitos is not None
    assert requisitos["usa_nombre_servicio"] is True


# ==============================================================================
# 3. Pruebas de Operaciones de Escritura (POST /api/items)
# ==============================================================================
def test_create_item_validation_empty_body(client):
    """Verifica que falle con HTTP 400 si se envía un cuerpo vacío."""
    response = client.post("/api/items", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_create_item_validation_missing_fields(client):
    """Verifica que falle con HTTP 400 si falta el título o la descripción."""
    response = client.post("/api/items", json={"titulo": "Solo titulo"})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

    response = client.post("/api/items", json={"descripcion": "Solo descripcion"})
    assert response.status_code == 400


def test_create_item_success(client, monkeypatch):
    """Verifica que una inserción válida retorne HTTP 201 y la estructura del registro guardado."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "id": 1,
        "titulo": "Prueba Pytest",
        "descripcion": "Descripción validada por prueba unitaria",
        "host_origen": "jenkins-runner",
        "creado_en": "2026-11-24 10:00:00"
    }
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    monkeypatch.setattr(main, "get_db_connection", lambda *args, **kwargs: mock_conn)

    payload = {
        "titulo": "Prueba Pytest",
        "descripcion": "Descripción validada por prueba unitaria"
    }
    response = client.post("/api/items", json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert "registro_guardado" in data
    assert data["registro_guardado"]["titulo"] == "Prueba Pytest"
    assert data["operacion"] == "INSERT persistido en volumen de datos"


# ==============================================================================
# 4. Pruebas de Operaciones de Lectura (GET /api/items)
# ==============================================================================
def test_get_items_success(client, monkeypatch):
    """Verifica la consulta de registros con HTTP 200 y formato de lista esperado."""
    mock_items = [
        {
            "id": 1,
            "titulo": "Item de Prueba 1",
            "descripcion": "Detalle 1",
            "host_origen": "host-1",
            "creado_en": "2026-11-24 09:00:00"
        },
        {
            "id": 2,
            "titulo": "Item de Prueba 2",
            "descripcion": "Detalle 2",
            "host_origen": "host-2",
            "creado_en": "2026-11-24 09:30:00"
        }
    ]
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_items
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    monkeypatch.setattr(main, "get_db_connection", lambda *args, **kwargs: mock_conn)

    response = client.get("/api/items")
    assert response.status_code == 200

    data = response.get_json()
    assert data["total"] == 2
    assert len(data["datos"]) == 2
    assert data["datos"][0]["titulo"] == "Item de Prueba 1"


def test_get_items_db_error(client, monkeypatch):
    """Verifica que un error en la base de datos retorne HTTP 500 adecuadamente formateado."""
    monkeypatch.setattr(main, "get_db_connection", lambda *args, **kwargs: (_ for _ in ()).throw(Exception("Error de conexión")))

    response = client.get("/api/items")
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data


# ==============================================================================
# 5. Prueba de Integración en Vivo (Si la BD PostgreSQL real está accesible)
# ==============================================================================
def test_live_database_roundtrip_if_available():
    """
    Prueba de integración real de ida y vuelta (Round-trip) hacia el contenedor 'db'.
    Se ejecuta automáticamente en el entorno CI (dentro de la red Docker) y se
    omite de forma segura en entornos locales sin contenedor activo.
    """
    try:
        conn = main.get_db_connection(max_retries=1, delay=0.5)
        if not conn:
            pytest.skip("Base de datos no disponible en este entorno (prueba unitaria aislada).")
    except Exception:
        pytest.skip("Base de datos no accesible en este entorno (prueba unitaria aislada).")

    with conn.cursor() as cur:
        # Prueba de escritura
        cur.execute("""
            INSERT INTO items (titulo, descripcion, host_origen)
            VALUES (%s, %s, %s)
            RETURNING id, titulo;
        """, ("Test Live Roundtrip", "Verificación automatizada de persistencia", "pytest-runner"))
        row = cur.fetchone()
        assert row is not None
        assert row["titulo"] == "Test Live Roundtrip"
        conn.commit()

        # Prueba de lectura
        cur.execute("SELECT count(*) as cnt FROM items;")
        count_res = cur.fetchone()
        assert count_res["cnt"] >= 1
    conn.close()
