"""Lógica de negocio para operaciones sobre PDFs.

Este módulo contiene la lógica pura sin conocimiento de HTTP ni bases de datos.
Los controllers son stateless y reutilizables tanto desde API REST como desde CLI.
"""

from dev.servers.models.pdf_document import Pdf
from dev.servers.services.pdf_extractor import PdfExtractor
from dev.servers.services.pdf_validator import (
    PdfNotFoundError,
    PdfValidationError,
    calculate_checksum,
    validate_pdf_bytes,
)


async def get_pdf_or_raise(pdf_id: str) -> Pdf:
    """Obtiene un PDF por ID o lanza PdfNotFoundError si no existe.

    Este es el único punto de traducción de "PDF no encontrado".
    Todos los métodos que consultan por ID usan este helper.

    Args:
        pdf_id: ID del PDF en MongoDB.

    Returns:
        El documento Pdf.

    Raises:
        PdfNotFoundError: Si el PDF no existe.
    """
    pdf = await Pdf.get(pdf_id)
    if not pdf:
        raise PdfNotFoundError(f"No existe un PDF con ID {pdf_id}")
    return pdf


async def get_pdf_by_checksum(checksum: str) -> Pdf | None:
    """Retorna un PDF existente si su checksum coincide, None en caso contrario."""
    return await Pdf.find_one({"checksum": checksum})


async def create_pdf(
    title: str,
    description: str | None,
    content: bytes,
    filename: str = "",
) -> Pdf:
    """Crea y persiste un documento PDF en la base de datos.

    Valida el contenido, calcula checksum, detecta duplicados y extrae texto.

    Args:
        title: Título del PDF.
        description: Descripción opcional.
        content: Contenido binario del PDF.
        filename: Nombre del archivo (para mensajes de error).

    Returns:
        El documento Pdf creado y persistido.

    Raises:
        PdfValidationError: Si el PDF no es válido o supera tamaño máximo.
    """
    # Validar formato y tamaño
    validate_pdf_bytes(content, filename)

    # Calcular checksum para detectar duplicados
    checksum = calculate_checksum(content)
    existing = await get_pdf_by_checksum(checksum)
    if existing:
        return existing

    # Extraer texto del PDF
    extractor = PdfExtractor()
    extracted_text = extractor.extract_text(content)

    # Crear y persistir documento
    pdf = Pdf(
        title=title,
        description=description,
        size=len(content),
        extracted_text=extracted_text,
        checksum=checksum,
    )
    await pdf.insert()
    return pdf


async def list_pdfs() -> list[Pdf]:
    """Retorna todos los PDFs ordenados por fecha de creación descendente."""
    return await Pdf.find().sort("-created_at").to_list()


async def delete_pdf(pdf_id: str) -> None:
    """Elimina un PDF existente. Lanza excepción si no existe."""
    pdf = await get_pdf_or_raise(pdf_id)
    await pdf.delete()


async def get_pdf_text(pdf_id: str) -> str:
    """Retorna el texto extraído de un PDF. Lanza excepción si no existe."""
    pdf = await get_pdf_or_raise(pdf_id)
    return pdf.extracted_text or ""