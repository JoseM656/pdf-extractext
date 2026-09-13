"""Entidad de dominio para documentos PDF.

Esta entidad es independiente de la persistencia: no conoce Beanie ni MongoDB.
Quien persiste son los adaptadores del puerto PdfRepository.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class PdfDocument(BaseModel):
    """Documento PDF tal como lo maneja la lógica de negocio."""

    id: str | None = None
    title: str
    description: str | None = None
    size: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Texto extraído del PDF en el momento del upload.
    # None significa que la extracción no se realizó o no produjo resultado.
    extracted_text: str | None = None

    # SHA-256 del contenido binario del archivo. Actúa como huella digital
    # del contenido real y se usa para detectar duplicados.
    checksum: str | None = None
