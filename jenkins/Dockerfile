# ==============================================================================
# Jenkins Controller personalizado con Docker CLI y Docker Compose
# Entrega Proyecto 2 - Integración Continua y DevOps
# Institución Universitaria Politécnico Grancolombiano
# ==============================================================================
FROM jenkins/jenkins:lts

# Cambiar temporalmente a usuario root para instalar paquetes del sistema operativo
USER root

# Instalar utilidades previas requeridas para agregar repositorios HTTPS
RUN apt-get update && apt-get install -y --no-install-recommends \
    lsb-release \
    curl \
    ca-certificates \
    gnupg \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Configurar el repositorio oficial de Docker CE en Debian
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker CLI oficial y el plugin oficial de Docker Compose (Docker-out-of-Docker)
RUN apt-get update && apt-get install -y --no-install-recommends \
    docker-ce-cli \
    docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

# Crear enlace simbólico para compatibilidad binaria ('docker-compose' y 'docker compose')
RUN ln -sf /usr/libexec/docker/cli-plugins/docker-compose /usr/local/bin/docker-compose

# Configurar grupo docker e incluir al usuario jenkins para acceso al socket /var/run/docker.sock
RUN groupadd -f docker && usermod -aG docker jenkins

# Retornar al usuario estándar de Jenkins
USER jenkins
