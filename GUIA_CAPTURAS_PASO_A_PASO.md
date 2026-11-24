# 📸 Guía Oficial de Capturas de Pantalla Paso a Paso
## Entrega 2: Integración Continua con Jenkins y Microservicios Docker
### Módulo: Integración Continua y DevOps — Politécnico Grancolombiano
**Integrantes:** Sebastián Salazar Urrego, Santiago Quintana Alvarado, Ronaldo Andrés Bautista Ruiz

---

## 🎯 Objetivo de esta Guía

La evidencia paso a paso es el criterio con mayor ponderación en la rúbrica de evaluación de la Entrega 2. Esta guía detalla la **lista numerada exacta** de cada captura que debe tomarse, el comando o URL requerido, qué elementos deben visualizarse y qué recuadro o texto debe resaltarse con un recuadro rojo para el evaluador.

---

## 📋 Lista Maestra de Capturas de Pantalla

| # | Título de la Evidencia | Entorno / URL / Comando | Criterio de la Rúbrica |
|---|------------------------|-------------------------|------------------------|
| **1** | Despliegue de Jenkins Controller en Docker | Terminal host: `docker compose -f docker-compose.jenkins.yml ps` | Jenkins desplegado en contenedor |
| **2** | Desbloqueo Inicial de Jenkins | `http://localhost:8080` + Terminal con `initialAdminPassword` | Configuración inicial del servidor |
| **3** | Plugins Requeridos Instalados | `http://localhost:8080/manage/pluginManager/installed` | Plugins de Pipeline, Git, Docker y Credentials |
| **4** | Credencial Secreta en Jenkins Store | `http://localhost:8080/manage/credentials/` | Manejo seguro de credenciales (Cero secretos) |
| **5** | Configuración del Job Pipeline y Poll SCM | `http://localhost:8080/job/docker-pipeline/configure` | Pipeline declarativo, Git SCM y disparador Poll SCM |
| **6** | Build 1: Ejecución Fallida (Simulación) | `http://localhost:8080/job/docker-pipeline/1/` | Evidencia de build fallido en Stage View |
| **7** | Consola del Build 1 Fallido | `http://localhost:8080/job/docker-pipeline/1/console` | Detalle del error y ejecución de bloque post |
| **8** | Build 2: Ejecución Exitosa (Corregida) | `http://localhost:8080/job/docker-pipeline/2/` | Build exitoso con todas las etapas en verde |
| **9** | Consola Build 2: Pruebas Pytest y Red 'db' | `http://localhost:8080/job/docker-pipeline/2/console` | Verificación de comunicación por servicio 'db' |
| **10** | Historial de Builds (Stage View) | `http://localhost:8080/job/docker-pipeline/` | Comparativa histórica (Rojo -> Verde) |
| **11** | Limpieza Post-Build en Host | Terminal host: `docker ps` | Comprobación de bloque `post { always }` |

---

## 🔍 Detalle Paso a Paso de Cada Captura

---

### 🔹 Captura 1: Despliegue de Jenkins Controller en Contenedor Docker

* **Comando a ejecutar:**
  ```bash
  docker compose -f docker-compose.jenkins.yml up -d --build
  docker compose -f docker-compose.jenkins.yml ps
  ```
* **Qué debe verse en la pantalla:**
  - La salida en consola mostrando la construcción de la imagen personalizada (`jenkins/Dockerfile`) con la instalación de Docker CLI y Docker Compose Plugin.
  - La tabla de `docker compose ps` mostrando el servicio `jenkins_server` en estado `Up` con los puertos `0.0.0.0:8080->8080/tcp` y `0.0.0.0:50000->50000/tcp`.
* **Elemento a resaltar para el evaluador:**
  - Recuadro rojo sobre el nombre `jenkins_server`, el estado `Up` y el mapeo de puertos `8080:8080`.
* **Justificación técnica:** Demuestra que Jenkins corre como contenedor aislado y no sobre el sistema operativo base, con acceso a `/var/run/docker.sock` para Docker-out-of-Docker.

---

### 🔹 Captura 2: Desbloqueo Inicial y Obtención de Contraseña Administradora

* **URL:** `http://localhost:8080`
* **Comando para obtener la clave:**
  ```bash
  docker exec jenkins_server cat /var/jenkins_home/secrets/initialAdminPassword
  ```
* **Qué debe verse en la pantalla:**
  - Ventana dividida o superpuesta: la interfaz web de Jenkins en la pantalla "Unlock Jenkins / Getting Started" y la consola de terminal con la clave de 32 caracteres alfanuméricos impresa.
* **Elemento a resaltar:**
  - La ruta `/var/jenkins_home/secrets/initialAdminPassword` en la UI y la salida coincidente en la terminal.
* **Justificación técnica:** Evidencia el arranque limpio de la instancia y la persistencia de datos en el volumen `jenkins_home_data`.

---

### 🔹 Captura 3: Plugins Requeridos Instalados y Verificados

* **URL:** `http://localhost:8080/manage/pluginManager/installed`
* **Qué debe verse en la pantalla:**
  - La sección de plugins instalados filtrando o buscando los componentes clave:
    1. **Pipeline** (`workflow-aggregator`)
    2. **Git** (`git`)
    3. **Docker Pipeline** (`docker-workflow`)
    4. **Credentials Binding Plugin** (`credentials-binding`)
    5. **Pipeline: Stage View Plugin** (`pipeline-stage-view`)
* **Elemento a resaltar:**
  - Los nombres de los 5 plugins listados con su estado activo (habilitado) y sus versiones.
* **Justificación técnica:** Da cumplimiento al criterio de la rúbrica referente a la instalación y verificación de plugins esenciales para pipelines declarativos con Docker y Git.

---

### 🔹 Captura 4: Configuración de Credencial Secreta en Jenkins Store

* **URL:** `http://localhost:8080/manage/credentials/store/system/domain/_/`
* **Procedimiento:**
  - Ir a: *Administrar Jenkins* -> *Credentials* -> *System* -> *Global credentials (unrestricted)* -> *Add Credentials*.
  - Tipo: **Secret text**.
  - Secret: `ci_testing_pass_2026` (o la contraseña de base de datos definida).
  - ID: `DB_PASSWORD`.
  - Descripción: `Credencial segura para base de datos PostgreSQL en CI`.
* **Qué debe verse en la pantalla:**
  - La tabla de credenciales globales mostrando la entrada `DB_PASSWORD`, tipo `Secret text`, con el valor enmascarado.
* **Elemento a resaltar:**
  - El campo ID: `DB_PASSWORD` y el tipo `Secret text`.
* **Justificación técnica:** Cumple con la regla de seguridad estricta: cero contraseñas en código o archivos compose; desacoplamiento total vía Jenkins Credentials.

---

### 🔹 Captura 5: Configuración del Pipeline Declarativo y Disparador Poll SCM

* **URL:** `http://localhost:8080/job/docker-microservicios-pipeline/configure`
* **Campos a configurar:**
  1. Sección **Disparadores de ejecuciones (Build Triggers)**:
     - Marcar: ☑ **Consultar repositorio (Poll SCM)**.
     - Horario (Schedule): `H/5 * * * *` (Sondeo cada 5 minutos).
  2. Sección **Pipeline**:
     - Definition: **Pipeline script from SCM**.
     - SCM: **Git**.
     - Repository URL: `https://github.com/ronaldo1124/docker-comunicacion-microservicios.git`
     - Branches to build: `*/main`
     - Script Path: `Jenkinsfile`
* **Qué debe verse en la pantalla:**
  - Ambas secciones visibles con las casillas activadas y las rutas configuradas.
* **Elemento a resaltar:**
  - La expresión cron `H/5 * * * *` de Poll SCM y el campo `Script Path: Jenkinsfile`.
* **Justificación técnica:** Evidencia la automatización del disparador por cambios en Git y la adopción de "Pipeline-as-Code".

---

### 🔹 Captura 6: Build 1 - Ejecución Fallida (Simulación en Stage View)

* **URL:** `http://localhost:8080/job/docker-microservicios-pipeline/`
* **Cómo simular el fallo:**
  - En la rama de pruebas o en el commit inicial, introducir un fallo intencional en la prueba (ejemplo: cambiar temporalmente en `test_app.py` `assert data["comunicacion_contenedor_destino"]["servicio_configurado"] == "db"` por `"db_incorrecto"` o modificar el nombre del host en `.env`).
  - Jenkins ejecuta el pipeline automáticamente vía Poll SCM o mediante "Construir ahora".
* **Qué debe verse en la pantalla:**
  - La vista de etapas **Stage View** mostrando:
    - Checkout: Verde
    - Environment Setup: Verde
    - Build: Verde
    - Deploy Services: Verde
    - **Test:** Recuadro **ROJO (Failed)** con el tiempo que tardó.
    - Post Actions: Recuadro Rojo o Ejecutado.
  - El ícono del Build `#1` con esfera roja parpadeante o fija.
* **Elemento a resaltar:**
  - El recuadro rojo en la etapa `Test` y el número `#1 (Failed)`.
* **Justificación técnica:** Requisito explícito de la rúbrica: evidenciar que el pipeline detecta anomalías y frena el ciclo ante errores en las pruebas de comunicación.

---

### 🔹 Captura 7: Consola del Build 1 Fallido y Ejecución del Bloque Post

* **URL:** `http://localhost:8080/job/docker-microservicios-pipeline/1/console`
* **Qué debe verse en la pantalla:**
  - La traza de consola mostrando el fallo exacto reportado por Pytest o el script de validación.
  - Inmediatamente abajo, la activación del bloque `post { failure { ... } }` imprimiendo los logs de `docker compose logs` y `post { always { ... } }` ejecutando `docker compose down -v`.
* **Elemento a resaltar:**
  - La aserción fallida de Pytest y la línea `[POST - FAILURE] Pipeline Fallido` ejecutando la limpieza de emergencia.
* **Justificación técnica:** Demuestra que la falla no deja recursos huérfanos y que el sistema provee trazabilidad para el diagnóstico.

---

### 🔹 Captura 8: Build 2 - Ejecución Exitosa tras Corrección (Todo en Verde)

* **URL:** `http://localhost:8080/job/docker-microservicios-pipeline/`
* **Procedimiento:**
  - Corregir el código en Git (restaurando la aserción correcta del servicio `db`).
  - Hacer `git commit -m "fix: corregir asercion de comunicacion inter-contenedor"` y `git push origin main`.
  - El Poll SCM detecta el push en los siguientes 5 minutos y lanza el Build `#2`.
* **Qué debe verse en la pantalla:**
  - La vista **Stage View** para el Build `#2` con **TODAS las etapas en color VERDE (Success)**:
    - `Checkout` (Verde)
    - `Environment Setup & Lint` (Verde)
    - `Build` (Verde)
    - `Deploy Services` (Verde)
    - `Test` (Verde)
    - `Declarative: Post Actions` (Verde)
* **Elemento a resaltar:**
  - Todas las columnas verdes del Build `#2` y el mensaje de éxito general.
* **Justificación técnica:** Cumple con la demostración de corrección de fallas y la aprobación integral del pipeline.

---

### 🔹 Captura 9: Consola de Pruebas Pytest y Comunicación por Nombre de Servicio 'db'

* **URL:** `http://localhost:8080/job/docker-microservicios-pipeline/2/consoleText` (o vista normal de consola)
* **Qué debe verse en la pantalla:**
  - Salida de Pytest:
    ```text
    tests/test_app.py::test_home_route PASSED
    tests/test_app.py::test_health_check_dns_and_service_name_success PASSED
    tests/test_app.py::test_health_check_when_db_unreachable PASSED
    tests/test_app.py::test_create_item_validation_empty_body PASSED
    tests/test_app.py::test_create_item_validation_missing_fields PASSED
    tests/test_app.py::test_create_item_success PASSED
    tests/test_app.py::test_get_items_success PASSED
    tests/test_app.py::test_get_items_db_error PASSED
    tests/test_app.py::test_live_database_roundtrip_if_available PASSED
    7 passed in 0.85s
    ```
  - La consulta al endpoint `/api/health` en formato JSON:
    ```json
    {
      "status": "healthy",
      "comunicacion_contenedor_destino": {
        "servicio_configurado": "db",
        "ip_resuelta_por_dns": "172.28.0.2",
        "conexion_establecida": true
      },
      "verificacion_requisitos": {
        "usa_nombre_servicio": true,
        "no_usa_localhost": true,
        "no_usa_ip_fija": true
      }
    }
    ```
  - Las operaciones de ida y vuelta:
    - POST `/api/items`: `HTTP 201 Created`
    - GET `/api/items`: `HTTP 200 OK` (con total de registros >= 1).
* **Elemento a resaltar:**
  - Las líneas `"servicio_configurado": "db"` y `"usa_nombre_servicio": true`.
* **Justificación técnica:** Evidencia técnica contundente del cumplimiento del criterio de comunicación inter-contenedor mediante nombre de servicio DNS en el entorno de integración continua.

---

### 🔹 Captura 10: Comparativa Histórica en Jenkins Stage View (Rojo -> Verde)

* **URL:** `http://localhost:8080/job/docker-microservicios-pipeline/`
* **Qué debe verse en la pantalla:**
  - La tabla completa del histórico de ejecuciones donde aparezcan en una sola pantalla:
    - Fila **#1**: Con la etapa Test en **Rojo** (Failed).
    - Fila **#2**: Con todas las etapas en **Verde** (Success).
  - La gráfica de tendencias de tiempo de ejecución (Average stage times).
* **Elemento a resaltar:**
  - El contraste directo entre la fila roja (#1) y la fila verde (#2).
* **Justificación técnica:** Sintetiza el cumplimiento de los puntos de la rúbrica sobre verificación de falla y corrección demostrable.

---

### 🔹 Captura 11: Verificación de Limpieza en Host (Bloque Post Always)

* **Comando a ejecutar en la terminal del host:**
  ```bash
  docker ps
  ```
* **Qué debe verse en la pantalla:**
  - La lista de contenedores activos en la máquina host.
  - Únicamente debe aparecer `jenkins_server` en ejecución.
  - Los contenedores temporales `app_service` y `db_service` ya no deben figurar, confirmando que la directiva `docker compose down -v` del bloque `post` se ejecutó con éxito.
* **Elemento a resaltar:**
  - Ausencia de contenedores huérfanos de la aplicación en la salida de `docker ps`.
* **Justificación técnica:** Demuestra la gestión higiénica de recursos en servidores de integración continua.

---

## 💡 Consejos para la Toma de Capturas

1. **Resolución uniforme:** Toma las capturas a 1920x1080 o ajustando el zoom del navegador (100% o 90%) para que los textos sean completamente legibles.
2. **Uso de recuadros:** Usa una herramienta como Recortes de Windows (Snipping Tool) o Flameshot para trazar un recuadro de color rojo (grosor 2px o 3px) sobre los puntos clave indicados arriba.
3. **Pega directa en Word:** El informe formal (`Informe_Proyecto2_Jenkins_Escenario5.docx`) generado en el repositorio incluye marcadores visuales y tablas prediseñadas para que sustituyas los recuadros de texto directamente por tus imágenes.
