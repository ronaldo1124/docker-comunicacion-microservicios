# Proyecto 1 (Escenario 3): Comunicación Inter-Contenedores con Docker

[![CI Docker Pipeline](https://github.com/ronaldo1124/docker-comunicacion-microservicios/actions/workflows/ci.yml/badge.svg)](https://github.com/ronaldo1124/docker-comunicacion-microservicios/actions/workflows/ci.yml)
![Docker](https://img.shields.io/badge/Docker-24.0+-2496ED?logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-v2-blue?logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11--slim-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16--alpine-336791?logo=postgresql&logoColor=white)
![Status](https://img.shields.io/badge/Entrega-100%25_Excelente-success)

> **Institución Universitaria Politécnico Grancolombiano**  
> **Facultad de Ingeniería, Diseño e Innovación**  
> **Módulo:** Integración Continua y DevOps  
> **Integrantes:**  
> - Sebastián Salazar Urrego (`ssalazaru@poligran.edu.co`)  
> - Santiago Quintana Alvarado (`squintana@poligran.edu.co`)  
> - Ronaldo Andrés Bautista Ruiz (`ranbautista@poligran.edu.co`)  
> **Entrega:** Proyecto 1 - Escenario 3 (150 Puntos)  

---

## 📋 Tabla de Contenidos
- [Descripción General](#-descripción-general)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Estructura del Repositorio](#-estructura-del-repositorio)
- [Detalle de los Contenedores](#-detalle-de-los-contenedores)
  - [Contenedor 1: Aplicación Web / API (app)](#contenedor-1-aplicación-web--api-app)
  - [Contenedor 2: Base de Datos Relacional (db)](#contenedor-2-base-de-datos-relacional-db)
- [Comunicación Inter-Contenedores (Criterio Central - 35 pts)](#-comunicación-inter-contenedores-criterio-central---35-pts)
- [Buenas Prácticas y Seguridad (15 pts)](#-buenas-prácticas-y-seguridad-15-pts)
- [Guía de Puesta en Marcha (Paso a Paso)](#-guía-de-puesta-en-marcha-paso-a-paso)
- [Comprobación de la Comunicación (Ida y Vuelta)](#-comprobación-de-la-comunicación-ida-y-vuelta)
- [Pipeline de CI con GitHub Actions (15 pts)](#-pipeline-de-ci-con-github-actions-15-pts)
- [Comandos Útiles de Docker](#-comandos-útiles-de-docker)

---

## 🚀 Descripción General

Este proyecto implementa una solución de microservicios contenerizados mediante **Docker** y **Docker Compose**, diseñada para demostrar la comunicación en red entre servicios aislados utilizando el **nombre de servicio** (`db`) y resolución DNS interna de Docker, evitando estrictamente el uso de `localhost` o direcciones IP fijas.

El sistema está compuesto por:
1. **Contenedor 1 (`app`):** Servicio web backend en Python 3.11 con Flask, interfaz interactiva y API REST.
2. **Contenedor 2 (`db`):** Base de datos relacional PostgreSQL 16 con persistencia de datos mediante volúmenes.
3. **Red Bridge propia (`red_interna_proyecto`):** Canal de red privado que provee aislamiento y servicio DNS embebido.
4. **Pipeline Automatizado (GitHub Actions):** Construye, valida y prueba de extremo a extremo la conectividad y persistencia en cada push o pull request.

---

## 🏗 Arquitectura del Sistema

```
+---------------------------------------------------------------------------------+
|                                HOST (Máquina Física)                            |
|                                                                                 |
|   Navegador Web / curl                                                          |
|   http://localhost:5000 --------------------+                                   |
|                                             | (Puerto 5000:5000)                |
+---------------------------------------------|-----------------------------------+
                                              |
+---------------------------------------------v-----------------------------------+
|               RED DOCKER TIPO BRIDGE (red_interna_proyecto)                     |
|                                                                                 |
|  +----------------------------+             +--------------------------------+  |
|  |       CONTENEDOR 1         |             |          CONTENEDOR 2          |  |
|  |     Servicio: 'app'        |  DNS: 'db'  |        Servicio: 'db'          |  |
|  |  (app_service: 172.x.x.3)  | ----------> |    (db_service: 172.x.x.2)     |  |
|  |                            |  Puerto     |                                |  |
|  |  * Python 3.11-slim        |   5432      |  * PostgreSQL 16-alpine        |  |
|  |  * Flask API & UI          |             |  * Healthcheck pg_isready      |  |
|  |  * Usuario sin privilegios | <---------- |  * Variables de entorno        |  |
|  +----------------------------+  Lectura    +--------------------------------+  |
|                                  y Datos                    |                   |
+-------------------------------------------------------------|-------------------+
                                                              |
                                                    +---------v---------+
                                                    |  VOLUMEN DOCKER   |
                                                    | (db_data_volumen) |
                                                    | Persistencia /data|
                                                    +-------------------+
```

---

## 📁 Estructura del Repositorio

La arquitectura sigue una separación estricta de responsabilidades por servicio:

```text
docker-comunicacion-microservicios/
├── .github/
│   └── workflows/
│       └── ci.yml                 # Pipeline de Integración Continua (GitHub Actions)
├── app/
│   ├── src/
│   │   ├── main.py                # Aplicación Flask, endpoints REST y pruebas de red
│   │   └── templates/
│   │       └── index.html         # Panel web interactivo con Tailwind CSS
│   ├── .dockerignore              # Exclusiones de construcción de imagen
│   ├── Dockerfile                 # Definición multicapa de la imagen base oficial
│   └── requirements.txt           # Dependencias fijadas (Flask, psycopg2-binary)
├── .env.example                   # Plantilla de variables de entorno (sin secretos)
├── .env                           # Variables locales (ignorado en Git por seguridad)
├── .gitignore                     # Exclusión de archivos sensibles y temporales
├── docker-compose.yml             # Orquestación de servicios, red y volumen
└── README.md                      # Documentación completa del proyecto
```

---

## 📦 Detalle de los Contenedores

### Contenedor 1: Aplicación Web / API (`app`)
* **Imagen base:** `python:3.11-slim` (Versión oficial y fija, no `latest`).
* **Optimización:** Variables `PYTHONDONTWRITEBYTECODE=1` y `PYTHONUNBUFFERED=1`.
* **Seguridad:** Usuario de sistema sin privilegios (`appuser`) que evita ejecutar procesos como `root`.
* **Caché:** Copia primero `requirements.txt` para acelerar builds posteriores.
* **Puerto expuesto:** `5000`.
* **Comando de inicio:** `CMD ["python", "src/main.py"]`.

### Contenedor 2: Base de Datos Relacional (`db`)
* **Imagen base:** `postgres:16-alpine` (Ligera, segura y oficial).
* **Variables de entorno:** `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` cargadas dinámicamente desde `.env`.
* **Persistencia:** Volumen nombrado `db_data` montado en `/var/lib/postgresql/data`.
* **Monitoreo:** `healthcheck` integrado con `pg_isready` para garantizar que la base de datos esté lista antes de que la aplicación empiece a recibir solicitudes.

---

## 🌐 Comunicación Inter-Contenedores (Criterio Central - 35 pts)

El requerimiento central exige que el **Contenedor 1** se comunique con el **Contenedor 2** utilizando el **nombre de servicio** (`db`) definido en el archivo `docker-compose.yml`.

### ¿Cómo funciona la resolución DNS interna?
1. Docker crea un servidor DNS embebido en la dirección `127.0.0.11` dentro del namespace de red de cada contenedor conectado a una red definida por el usuario.
2. Cuando `app` se conecta a la base de datos, utiliza `DB_HOST=db`.
3. El sistema operativo del contenedor consulta a `127.0.0.11`, el cual responde dinámicamente con la IP interna del contenedor `db` dentro de la red `red_interna_proyecto` (por ejemplo, `172.28.0.2`).
4. **Cumplimiento estricto:** No se utiliza `localhost` (lo cual fallaría ya que cada contenedor tiene su propio loopback) ni una IP fija (lo cual violaría las buenas prácticas de despliegue dinámico).

---

## 🔒 Buenas Prácticas y Seguridad (15 pts)

1. **Gestión de Secretos:**
   - Se incluye un archivo `.env.example` en el repositorio con credenciales de muestra.
   - El archivo `.env` real está estrictamente ignorado mediante `.gitignore` para evitar fugas de información sensible.
   - En el código fuente (`main.py`) no hay contraseñas en texto plano; todo se recupera mediante `os.getenv()`.
2. **Contexto de Construcción Limpio:**
   - El archivo `.dockerignore` previene que archivos locales temporales (`.git`, `__pycache__`, `.env`, documentación) inflen la imagen de Docker.
3. **Principio de Mínimo Privilegio:**
   - La aplicación corre bajo el usuario no privilegiado `appuser`, mitigando riesgos de seguridad en caso de vulnerabilidades en el runtime.
4. **Imágenes fijadas:**
   - Uso de tags semánticos exactos (`python:3.11-slim` y `postgres:16-alpine`), evitando la etiqueta volátil `latest`.

---

## 🛠 Guía de Puesta en Marcha (Paso a Paso)

### 1. Clonar el repositorio
```bash
git clone https://github.com/ronaldo1124/docker-comunicacion-microservicios.git
cd docker-comunicacion-microservicios
```

### 2. Configurar las variables de entorno
```bash
# En Windows (PowerShell)
Copy-Item .env.example .env

# En Linux / macOS
cp .env.example .env
```

*(Opcional: puedes editar `.env` si deseas cambiar las contraseñas predeterminadas).*

### 3. Construir y levantar los contenedores
Ejecuta el siguiente comando para construir la imagen del contenedor 1 y levantar toda la arquitectura en segundo plano:
```bash
docker compose up --build -d
```

### 4. Verificar el estado de los contenedores
```bash
docker compose ps
```
Deberás observar ambos contenedores (`app_service` y `db_service`) en estado `Up` (o `healthy`).

### 5. Inspeccionar la red privada de Docker
Para evidenciar que ambos contenedores comparten la misma red y observar sus IPs asignadas:
```bash
docker network inspect red_interna_proyecto
```

---

## 🧪 Comprobación de la Comunicación (Ida y Vuelta)

Puedes realizar las pruebas desde la **interfaz gráfica en el navegador** o mediante **comandos en la terminal**.

### Opción A: Desde el Navegador Web
Abre tu navegador e ingresa a:
👉 **[http://localhost:5000](http://localhost:5000)**

En el panel interactivo podrás:
* Ver el estado en tiempo real de la conexión con el contenedor `db`.
* Consultar la IP resuelta por el DNS interno de Docker.
* Llenar el formulario para enviar un registro (**POST** hacia PostgreSQL).
* Visualizar en la tabla la lectura inmediata del registro (**GET** desde PostgreSQL).

---

### Opción B: Desde la Terminal (Pruebas Automatizadas)

#### 1. Probar el diagnóstico y healthcheck de red:
```bash
curl -s http://localhost:5000/api/health
```
*Respuesta esperada (JSON):*
```json
{
  "status": "healthy",
  "comunicacion_contenedor_destino": {
    "servicio_configurado": "db",
    "ip_resuelta_por_dns": "172.28.0.2",
    "conexion_establecida": true,
    "dns_mecanismo": "Resolución DNS exitosa mediante Docker Embedded DNS"
  },
  "verificacion_requisitos": {
    "usa_nombre_servicio": true,
    "no_usa_localhost": true,
    "no_usa_ip_fija": true
  }
}
```

#### 2. Operación de Escritura (Ida hacia Contenedor 2):
```bash
curl -X POST http://localhost:5000/api/items \
  -H "Content-Type: application/json" \
  -d "{\"titulo\": \"Prueba de conexion\", \"descripcion\": \"Mensaje guardado en PostgreSQL via servicio db\"}"
```

#### 3. Operación de Lectura (Vuelta desde Contenedor 2):
```bash
curl -s http://localhost:5000/api/items
```

---

## 🔄 Demostración de Persistencia de Datos (Volumen)

Para validar que el volumen `db_data` retiene la información tras destruir los contenedores:

1. Agrega varios registros mediante el panel web o curl.
2. Detén y elimina los contenedores (sin borrar el volumen):
   ```bash
   docker compose down
   ```
3. Vuelve a iniciar los contenedores:
   ```bash
   docker compose up -d
   ```
4. Ingresa a `http://localhost:5000` o ejecuta `curl http://localhost:5000/api/items`. Los datos guardados previamente siguen intactos.

---

## ⚙️ Pipeline de CI con GitHub Actions (15 pts)

El archivo [`.github/workflows/ci.yml`](.github/workflows/ci.yml) se ejecuta automáticamente en cada `push` o `pull_request` a la rama principal.

El pipeline realiza de forma desatendida:
1. Validación sintáctica de `docker-compose.yml` (`docker compose config`).
2. Construcción de la imagen del Contenedor 1 (`docker compose build`).
3. Despliegue de los servicios (`docker compose up -d`).
4. Verificación de salud y estado de la red.
5. Ejecución de pruebas de comunicación de ida y vuelta (POST y GET con `curl`).
6. Verificación de código de retorno exitoso (check en verde).

---

## 📑 Comandos Útiles de Docker

| Acción | Comando |
| :--- | :--- |
| **Construir y levantar servicios** | `docker compose up --build -d` |
| **Ver estado de contenedores** | `docker compose ps` |
| **Ver logs en tiempo real** | `docker compose logs -f` |
| **Ver logs específicos de la app** | `docker compose logs -f app` |
| **Ver logs específicos de la base de datos** | `docker compose logs -f db` |
| **Inspeccionar la red bridge** | `docker network inspect red_interna_proyecto` |
| **Inspeccionar el volumen de datos** | `docker volume inspect db_data_volumen` |
| **Detener contenedores (manteniendo datos)** | `docker compose down` |
| **Detener y eliminar volúmenes (reset total)** | `docker compose down -v` |

---

## 👨‍💻 Integrantes del Equipo
* **Sebastián Salazar Urrego** — `ssalazaru@poligran.edu.co`
* **Santiago Quintana Alvarado** — `squintana@poligran.edu.co`
* **Ronaldo Andrés Bautista Ruiz** — `ranbautista@poligran.edu.co` | GitHub: [@ronaldo1124](https://github.com/ronaldo1124)

* **Programa:** Ingeniería de Sistemas
* **Institución:** Institución Universitaria Politécnico Grancolombiano
