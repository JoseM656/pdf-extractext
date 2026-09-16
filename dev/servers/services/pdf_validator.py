"""Validaciones de formato y tamaño para archivos PDF.

Este módulo centraliza las reglas de validación para que tanto
el CLI como la API REST las reutilicen sin duplicar lógica (DRY).
"""

import hashlib

from dev.config import settings

PDF_MAGIC_BYTES = b"%PDF-"


class PdfValidationError(ValueError):
    """Excepción que se lanza cuando un archivo no supera la validación."""


class PdfNotFoundError(ValueError):
    """Excepción que se lanza cuando un PDF no existe en la base de datos."""

class DuplicatePdfError(ValueError):
    """Excepción que se lanza cuando ya existe un PDF con el mismo checksum.
 
    Guarda el `existing_id` del documento ya registrado para que quien
    atrape la excepción (el router) pueda informarlo sin tener que volver
    a consultar el repositorio.
    """
 
    def __init__(self, existing_id: str) -> None:
        self.existing_id = existing_id
        super().__init__(f"Ya existe un PDF con este contenido (id={existing_id}).")


def calculate_checksum(content: bytes) -> str:
    """Calcula el checksum SHA-256 del contenido binario."""
    return hashlib.sha256(content).hexdigest()


def validate_pdf_bytes(content: bytes, filename: str = "") -> None:
    """Valida que el contenido binario corresponda a un PDF válido y dentro del tamaño permitido.

    Args:
        content: Bytes del archivo a validar.
        filename: Nombre del archivo (opcional, solo para mensajes de error).

    Raises:
        PdfValidationError: Si el archivo no es un PDF o supera el tamaño máximo.
    """
    _check_magic_bytes(content, filename)
    _check_file_size(content, filename)


def _check_magic_bytes(content: bytes, filename: str) -> None:
    """Verifica que el contenido comience con los magic bytes de PDF."""
    if not content.startswith(PDF_MAGIC_BYTES):
        raise PdfValidationError(
            f"El archivo '{filename}' no es un PDF válido. "
            f"Se esperaba que comenzara con '{PDF_MAGIC_BYTES.decode()}'."
        )


def _check_file_size(content: bytes, filename: str) -> None:
    """Verifica que el contenido no supere el tamaño máximo configurado."""
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise PdfValidationError(
            f"El archivo '{filename}' supera el tamaño máximo permitido "
            f"({settings.MAX_FILE_SIZE_MB} MB). "
            f"Tamaño actual: {len(content) / 1024 / 1024:.1f} MB."
        )
        