from typing import Annotated

from beanie import Document, Indexed
from datetime import datetime
from pydantic import Field


class Pdf(Document):
    title: str
    description: str | None = None
    path: str
    size: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Texto extraído del PDF en el momento del upload.
    # Se persiste aquí para no necesitar el archivo original después.
    # None significa que la extracción no se realizó o no produjo resultado.
    extracted_text: str | None = None

    # SHA-256 del contenido binario del archivo.
    # Actúa como huella digital del contenido real, independiente del nombre.
    # Se usa para detectar duplicados antes de persistir un nuevo documento.
    # Annotated + Indexed es la forma correcta de declarar índices en Beanie
    # manteniendo compatibilidad con el sistema de tipos de Python.
    checksum: Annotated[str, Indexed(unique=True)] | None = None

    class Settings:
        name = "pdfs"