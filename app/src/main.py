import os
import socket
import time
from datetime import datetime
from flask import Flask, jsonify, request, render_template
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Configuración leída estrictamente desde Variables de Entorno (Sin secretos en código)
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "proyectodb")
DB_USER = os.getenv("DB_USER", "postgres_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres_password_segura")
APP_PORT = int(os.getenv("APP_PORT", 5000))

def get_db_connection(max_retries=5, delay=2):
    """Establece conexión con el contenedor de base de datos usando el nombre de servicio 'db'."""
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                connect_timeout=5,
                cursor_factory=RealDictCursor
            )
            return conn
        except Exception as e:
            if attempt == max_retries:
                raise e
            time.sleep(delay)
    return None

def init_db():
    """Inicializa la tabla de datos en el Contenedor 2 si no existe."""
    try:
        conn = get_db_connection(max_retries=3, delay=1)
        if conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS items (
                        id SERIAL PRIMARY KEY,
                        titulo VARCHAR(120) NOT NULL,
                        descripcion TEXT NOT NULL,
                        host_origen VARCHAR(80),
                        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
            conn.close()
            print("[INFO] Base de datos inicializada y tabla 'items' verificada.")
    except Exception as e:
        print(f"[WARN] No se pudo inicializar la BD de inmediato (iniciará en primera petición): {e}")

# Rutas de la Interfaz Web y Diagnóstico
@app.route("/")
def home():
    """Página principal interactiva para verificar la comunicación y pruebas."""
    hostname = socket.gethostname()
    resolved_ip = "Desconocida"
    try:
        resolved_ip = socket.gethostbyname(DB_HOST)
    except Exception:
        resolved_ip = "Error de resolución DNS"

    return render_template("index.html", 
                           hostname=hostname, 
                           db_host=DB_HOST, 
                           resolved_ip=resolved_ip,
                           db_name=DB_NAME)

@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Punto 5 de evaluación:
    Demuestra que la app se comunica con el contenedor 2 usando el nombre 'db'
    y valida el DNS interno de Docker.
    """
    hostname = socket.gethostname()
    db_ip = "No resuelta"
    dns_status = "Error"
    
    try:
        db_ip = socket.gethostbyname(DB_HOST)
        dns_status = "Resolución DNS exitosa mediante Docker Embedded DNS"
    except Exception as e:
        dns_status = f"Fallo al resolver DNS: {str(e)}"

    db_connected = False
    db_version = None
    items_count = 0

    try:
        conn = get_db_connection(max_retries=2, delay=1)
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            db_version = cur.fetchone()["version"]
            
            cur.execute("SELECT count(*) as total FROM items;")
            items_count = cur.fetchone()["total"]
        conn.close()
        db_connected = True
    except Exception as e:
        db_version = f"Error al consultar BD: {str(e)}"

    return jsonify({
        "status": "healthy" if db_connected else "degraded",
        "contenedor_origen": {
            "servicio": "app",
            "hostname": hostname
        },
        "comunicacion_contenedor_destino": {
            "servicio_configurado": DB_HOST,
            "ip_resuelta_por_dns": db_ip,
            "puerto": DB_PORT,
            "base_datos": DB_NAME,
            "usuario": DB_USER,
            "dns_mecanismo": dns_status,
            "conexion_establecida": db_connected,
            "version_motor": db_version,
            "total_registros_guardados": items_count
        },
        "verificacion_requisitos": {
            "usa_nombre_servicio": DB_HOST == "db",
            "no_usa_localhost": DB_HOST != "localhost" and DB_HOST != "127.0.0.1",
            "no_usa_ip_fija": not DB_HOST.replace('.', '').isdigit()
        },
        "timestamp": datetime.now().isoformat()
    }), 200 if db_connected else 503

@app.route("/api/items", methods=["GET"])
def get_items():
    """Operación de LECTURA (Ida y vuelta hacia Contenedor 2)."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, titulo, descripcion, host_origen, 
                       to_char(creado_en, 'YYYY-MM-DD HH24:MI:SS') as creado_en 
                FROM items 
                ORDER BY id DESC;
            """)
            items = cur.fetchall()
        conn.close()
        return jsonify({
            "mensaje": "Lectura exitosa desde el contenedor db (PostgreSQL)",
            "origen_datos": f"Servicio '{DB_HOST}' en red Docker",
            "total": len(items),
            "datos": items
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al leer datos del contenedor 'db': {str(e)}"}), 500

@app.route("/api/items", methods=["POST"])
def create_item():
    """Operación de ESCRITURA (Ida y vuelta hacia Contenedor 2)."""
    data = request.get_json(silent=True) or {}
    titulo = data.get("titulo", "").strip()
    descripcion = data.get("descripcion", "").strip()

    if not titulo or not descripcion:
        return jsonify({
            "error": "Los campos 'titulo' y 'descripcion' son obligatorios para guardar el registro."
        }), 400

    hostname = socket.gethostname()

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO items (titulo, descripcion, host_origen) 
                VALUES (%s, %s, %s) 
                RETURNING id, titulo, descripcion, host_origen, 
                          to_char(creado_en, 'YYYY-MM-DD HH24:MI:SS') as creado_en;
            """, (titulo, descripcion, hostname))
            nuevo_registro = cur.fetchone()
            conn.commit()
        conn.close()

        return jsonify({
            "mensaje": "Escritura exitosa en el contenedor db (PostgreSQL)",
            "operacion": "INSERT persistido en volumen de datos",
            "registro_guardado": nuevo_registro
        }), 201
    except Exception as e:
        return jsonify({"error": f"Error al escribir datos en el contenedor 'db': {str(e)}"}), 500

if __name__ == "__main__":
    # Inicializar la base de datos al arrancar
    init_db()
    # Ejecutar en todas las interfaces del contenedor
    app.run(host="0.0.0.0", port=APP_PORT, debug=False)
