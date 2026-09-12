"""Validaciones de formato y tamaño para archivos PDF.

Este módulo centraliza las reglas de validación para que tanto
el CLI como la API REST las reutilicen sin duplicar lógica (DRY).
"""

from dev.config import settings

# Los PDF siempre comienzan con estos bytes ("magic bytes").
# Es la forma estándar de verificar el formato real del archivo,
# independientemente de la extensión que tenga el nombre.
PDF_MAGIC_BYTES = b"%PDF-"


class PdfValidationError(ValueError):
    """Excepción que se lanza cuando un archivo no supera la validación."""


class PdfNotFoundError(ValueError):
    """Excepción que se lanza cuando un PDF no existe en la base de datos."""


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
        