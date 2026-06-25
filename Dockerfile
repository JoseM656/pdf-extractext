FROM python:3.12-slim

# Instalar uv copiando los binarios oficiales.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Instalar herramientas de monitoreo antes de sincronizar dependencias.
# Se hace en una sola capa RUN para no inflar el tamaño de la imagen.
RUN apt-get update && \
    apt-get install -y --no-install-recommends htop procps && \
    rm -rf /var/lib/apt/lists/*

# Directorio de trabajo interno
WORKDIR /app

# Copiar los archivos de bloqueo Y el README requerido por el backend de compilación
COPY pyproject.toml uv.lock README.md ./

# Copiar el código fuente
COPY dev/ ./dev

# Instalar usando el uv.lock de forma exacta (crea /app/.venv)
RUN uv sync --frozen --no-dev --no-editable

# SEGURIDAD: Crear usuario no-root para ejecución segura.
RUN useradd -u 10001 -m appuser && chown -R appuser:appuser /app
USER appuser

# Exponer el puerto nativo de FastAPI.
EXPOSE 8000

# Comando de arranque apuntando al entorno virtual generado por uv
CMD ["/app/.venv/bin/uvicorn", "dev.servers.app:app", "--host", "0.0.0.0", "--port", "8000"]