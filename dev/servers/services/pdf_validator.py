"""Validaciones de formato y tamaño para archivos PDF.

Este módulo centraliza las reglas de validación para que tanto
el CLI como la API REST las reutilicen sin duplicar lógica (DRY).
"""

from pathlib import Path

from dev.config import settings

# Los PDF siempre comienzan con estos bytes ("magic bytes").
# Es la forma estándar de verificar el formato real del archivo,
# independientemente de la extensión que tenga el nombre.
PDF_MAGIC_BYTES = b"%PDF-"


class PdfValidationError(ValueError):
    """Excepción que se lanza cuando un archivo no supera la validación."""


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


def validate_pdf_path(pdf_path: Path) -> None:
    """Valida un PDF a partir de su ruta en disco.

    Lee solo los primeros bytes para la validación de formato,
    y usa el tamaño del filesystem para la validación de tamaño,
    evitando cargar el archivo completo en memoria innecesariamente.

    Args:
        pdf_path: Ruta al archivo PDF.

    Raises:
        PdfValidationError: Si el archivo no es un PDF o supera el tamaño máximo.
    """
    # Leemos solo los primeros bytes para verificar el magic number
    with pdf_path.open("rb") as f:
        header = f.read(len(PDF_MAGIC_BYTES))

    _check_magic_bytes(header, pdf_path.name)

    # Para el tamaño usamos el filesystem, no cargamos el archivo completo
    file_size = pdf_path.stat().st_size
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise PdfValidationError(
            f"El archivo '{pdf_path.name}' supera el tamaño máximo permitido "
            f"({settings.MAX_FILE_SIZE_MB} MB). Tamaño actual: {file_size / 1024 / 1024:.1f} MB."
        )


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