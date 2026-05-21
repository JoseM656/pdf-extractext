FROM python:3.12-slim

# Instalar uv copiando los binarios oficiales.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Directorio de trabajo interno
WORKDIR /app

# Copiar archivos de dependencias y el código de la app.
COPY pyproject.toml uv.lock README.md ./
COPY dev/ ./dev

# Copiar el código fuente
COPY dev/ ./dev

# Instalar las dependencias directamente en el entorno del contenedor
RUN uv pip install --system --no-cache .

# SEGURIDAD: Crear usuario no-root para ejecución segura.
RUN useradd -u 10001 -m appuser && chown -R appuser:appuser /app
USER appuser

# Exponer el puerto nativo de FastAPI.
EXPOSE 8000

# Comando de arranque para producción.
CMD ["uvicorn", "dev.servers.app:app", "--host", "0.0.0.0", "--port", "8000"]