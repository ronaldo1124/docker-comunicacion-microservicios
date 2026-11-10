# ==============================================================================
# Contenedor 1: Aplicación Web / API REST (Python + Flask)
# Imagen base oficial con versión fija (no «latest») - Requisito 2
# ==============================================================================
FROM python:3.11-slim

# Metadatos del contenedor
LABEL maintainer="Ronaldo Bautista <ronaldo.bautistar@outlook.com>"
LABEL description="Contenedor 1 - Aplicación Flask para comunicación con PostgreSQL"

# Variables de entorno para optimización de ejecución de Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Directorio de trabajo
WORKDIR /app

# Crear usuario y grupo de sistema sin privilegios (Buenas prácticas de seguridad)
RUN addgroup --system appgroup && adduser --system --group appuser

# Copiar primero el archivo de requerimientos (aprovechamiento de capa de caché)
COPY requirements.txt .

# Instalar dependencias oficiales sin almacenar caché de pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente de la aplicación
COPY src/ ./src/

# Asignar permisos al usuario no root
RUN chown -R appuser:appgroup /app

# Cambiar al usuario no root
USER appuser

# Exponer el puerto configurado
EXPOSE 5000

# Comando de inicio del contenedor
CMD ["python", "src/main.py"]
