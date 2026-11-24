// ==============================================================================
// Jenkinsfile Declarativo - Pipeline CI/CD para Microservicios Docker
// Entrega Proyecto 2 - Integración Continua y DevOps
// Institución Universitaria Politécnico Grancolombiano
// Estudiante: Ronaldo Andrés Bautista Ruiz
// ==============================================================================

pipeline {
    agent any

    // Disparadores automáticos: Polling SCM cada 5 minutos
    triggers {
        pollSCM('H/5 * * * *')
    }

    // Manejo de variables de entorno y credenciales seguras
    environment {
        // Credencial administrada de forma segura mediante Jenkins Credentials Plugin
        // Enmascarada automáticamente (****) en los logs de consola
        DB_PASSWORD = credentials('DB_PASSWORD')
        DB_HOST = 'db'
        DB_PORT = '5432'
        DB_EXTERNAL_PORT = '5432'
        DB_NAME = 'proyectodb'
        DB_USER = 'postgres_user'
        APP_PORT = '5000'
    }

    stages {
        // ----------------------------------------------------------------------
        // Etapa 1: Checkout de Código Fuente
        // ----------------------------------------------------------------------
        stage('Checkout') {
            steps {
                echo '=================================================='
                echo ' [ETAPA 1] Checkout de Código Fuente'
                echo '=================================================='
                checkout scm
                sh '''
                    echo "[INFO] Rama y commit actual:"
                    git log -1 --pretty=format:"Commit: %h - Autor: %an - Mensaje: %s (%cd)"
                    echo ""
                '''
            }
        }

        // ----------------------------------------------------------------------
        // Etapa 2: Configuración del Entorno y Validación Sintáctica
        // ----------------------------------------------------------------------
        stage('Environment Setup & Lint') {
            steps {
                echo '=================================================='
                echo ' [ETAPA 2] Configuración de Entorno y Validación'
                echo '=================================================='
                sh '''
                    echo "[INFO] Generando archivo .env a partir de .env.example..."
                    cp .env.example .env

                    # Inyección segura de la credencial DB_PASSWORD
                    if [ -n "$DB_PASSWORD" ]; then
                        echo "[INFO] Inyectando credencial secreta DB_PASSWORD en .env..."
                        sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" .env
                    else
                        echo "[WARN] DB_PASSWORD no detectada; usando credencial de fallback segura para CI..."
                        sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=ci_testing_pass_2026/" .env
                    fi

                    echo "[INFO] Validando sintaxis y modelo de docker-compose.yml..."
                    docker compose config
                '''
            }
        }

        // ----------------------------------------------------------------------
        // Etapa 3: Construcción de Imágenes Docker (Build)
        // ----------------------------------------------------------------------
        stage('Build') {
            steps {
                echo '=================================================='
                echo ' [ETAPA 3] Construcción de Imágenes Docker (Build)'
                echo '=================================================='
                sh '''
                    echo "[INFO] Construyendo imágenes de los microservicios sin caché..."
                    docker compose build --no-cache
                    echo "[OK] Imágenes construidas exitosamente."
                '''
            }
        }

        // ----------------------------------------------------------------------
        // Etapa 4: Despliegue de Servicios y Verificación de Red
        // ----------------------------------------------------------------------
        stage('Deploy Services') {
            steps {
                echo '=================================================='
                echo ' [ETAPA 4] Despliegue de Servicios en Red Bridge'
                echo '=================================================='
                sh '''
                    echo "[INFO] Levantando contenedores en segundo plano..."
                    docker compose up -d

                    echo "[INFO] Esperando estado saludable (healthy) de db_service (pg_isready)..."
                    for i in $(seq 1 30); do
                        STATUS=$(docker inspect --format='{{json .State.Health.Status}}' db_service 2>/dev/null || echo '"starting"')
                        echo "Intento $i/30: Estado del contenedor 'db': $STATUS"
                        if [ "$STATUS" = '"healthy"' ]; then
                            echo "[OK] Contenedor PostgreSQL 16 listo y saludable."
                            break
                        fi
                        sleep 2
                    done

                    echo "[INFO] Listando estado actual de los contenedores:"
                    docker compose ps

                    echo "[INFO] Inspeccionando la red privada red_interna_proyecto:"
                    docker network inspect red_interna_proyecto
                '''
            }
        }

        // ----------------------------------------------------------------------
        // Etapa 5: Pruebas Unitarias y Verificación de Comunicación Inter-Contenedor
        // ----------------------------------------------------------------------
        stage('Test') {
            steps {
                echo '=================================================='
                echo ' [ETAPA 5] Pruebas Unitarias y de Comunicación'
                echo '=================================================='

                // 1. Pruebas Automatizadas con Pytest dentro del Contenedor de la Aplicación
                echo '>>> 1. Ejecución de Pruebas Unitarias Automatizadas (Pytest) <<<'
                sh '''
                    echo "[INFO] Ejecutando suite de pruebas en app_service..."
                    docker compose exec -T app pytest tests/test_app.py -v --tb=short
                '''

                // 2. Verificación de Comunicación por Nombre de Servicio 'db'
                echo '>>> 2. Verificación de Comunicación por Nombre de Servicio "db" <<<'
                sh '''
                    echo "[INFO] Esperando disponibilidad de la API Flask en http://localhost:5000..."
                    for i in $(seq 1 20); do
                        if docker compose exec -T app curl -s -f http://localhost:5000/api/health >/dev/null 2>&1; then
                            echo "[OK] API Flask en línea y respondiendo."
                            break
                        fi
                        sleep 1
                    done

                    echo "[INFO] Consultando endpoint de diagnóstico /api/health..."
                    HEALTH=$(docker compose exec -T app curl -s http://localhost:5000/api/health)
                    echo "$HEALTH"

                    # Validar resolución DNS y nombre de servicio 'db'
                    SERVICE_CFG=$(docker compose exec -T app python -c "import json; d=json.loads('''$HEALTH'''); print(d['comunicacion_contenedor_destino']['servicio_configurado'])")
                    IP_RES=$(docker compose exec -T app python -c "import json; d=json.loads('''$HEALTH'''); print(d['comunicacion_contenedor_destino']['ip_resuelta_por_dns'])")
                    REQ_NAME=$(docker compose exec -T app python -c "import json; d=json.loads('''$HEALTH'''); print(d['verificacion_requisitos']['usa_nombre_servicio'])")
                    REQ_NO_LOCAL=$(docker compose exec -T app python -c "import json; d=json.loads('''$HEALTH'''); print(d['verificacion_requisitos']['no_usa_localhost'])")

                    echo "[INFO] Servicio configurado: $SERVICE_CFG"
                    echo "[INFO] IP resuelta por DNS: $IP_RES"

                    if [ "$SERVICE_CFG" != "db" ]; then
                        echo "[ERROR] El servicio configurado no es 'db'"
                        exit 1
                    fi
                    if [ "$REQ_NAME" != "True" ] || [ "$REQ_NO_LOCAL" != "True" ]; then
                        echo "[ERROR] Falló la verificación de requisitos de comunicación inter-contenedor"
                        exit 1
                    fi
                    echo "[OK] Verificación de comunicación por nombre de servicio 'db' exitosa."
                '''

                // 3. Demostración de Comunicación de Ida y Vuelta (POST y GET)
                echo '>>> 3. Comunicación de Ida y Vuelta (Escritura POST y Lectura GET) <<<'
                sh '''
                    echo "[INFO] Realizando operación de Escritura (POST /api/items)..."
                    POST_RESP=$(docker compose exec -T app curl -s -X POST http://localhost:5000/api/items \
                        -H "Content-Type: application/json" \
                        -d '{"titulo": "Registro Jenkins CI/CD", "descripcion": "Validación de ida y vuelta en pipeline automatizado"}')
                    echo "$POST_RESP"

                    echo "[INFO] Realizando operación de Lectura (GET /api/items)..."
                    GET_RESP=$(docker compose exec -T app curl -s http://localhost:5000/api/items)
                    echo "$GET_RESP"

                    TOTAL=$(docker compose exec -T app python -c "import json; d=json.loads('''$GET_RESP'''); print(d['total'])")
                    if [ "$TOTAL" -lt 1 ]; then
                        echo "[ERROR] No se encontraron registros persistidos en la base de datos"
                        exit 1
                    fi
                    echo "[OK] Flujo de ida y vuelta completado con $TOTAL registros persistidos."
                '''
            }
        }
    }

    // --------------------------------------------------------------------------
    // Bloque Post: Limpieza y Reportes de Ejecución
    // --------------------------------------------------------------------------
    post {
        always {
            echo '=================================================='
            echo ' [POST - ALWAYS] Limpieza de Recursos y Volúmenes'
            echo '=================================================='
            sh '''
                echo "[INFO] Apagando y destruyendo contenedores y volúmenes de prueba..."
                docker compose down -v || true
            '''
        }
        success {
            echo '=================================================='
            echo ' [POST - SUCCESS] Pipeline Completado con Éxito'
            echo ' Todos los criterios técnicos de Entrega 2 aprobados.'
            echo '=================================================='
        }
        failure {
            echo '=================================================='
            echo ' [POST - FAILURE] Pipeline Fallido'
            echo ' Extrayendo logs de diagnóstico de los contenedores...'
            echo '=================================================='
            sh '''
                docker compose logs || true
            '''
        }
    }
}
