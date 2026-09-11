"""Lógica de negocio para operaciones sobre PDFs.
 
Este módulo contiene la lógica pura sin conocimiento de HTTP ni bases de datos.
Los controllers son stateless y reutilizables tanto desde API REST como desde CLI.
"""

from dev.servers.models.pdf_document import Pdf
from dev.servers.services.pdf_validator import PdfNotFoundError


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


async def create_pdf(
    title: str,
    description: str | None,
    size: int,
    extracted_text: str | None = None,
    checksum: str | None = None,
) -> Pdf:
    """Crea y persiste un documento PDF en la base de datos."""
    pdf = Pdf(
        title=title,
        description=description,
        size=size,
        extracted_text=extracted_text,
        checksum=checksum,
    )
    await pdf.insert()
    return pdf


async def get_pdf_by_checksum(checksum: str) -> Pdf | None:
"""Retorna un PDF existente si su checksum coincide, None en caso contrario."""
    return await Pdf.find_one({"checksum" : checksum})


async def list_pdfs() -> list[Pdf]:
    """Retorna todos los PDFs ordenados por fecha de creación descendente."""
    return await Pdf.find().sort(-Pdf.created_at).to_list()


async def delete_pdf(pdf_id: str) -> None:
"""Elimina un PDF existente. Lanza excepción si no existe."""
    pdf = await get_pdf_or_raise(pdf_id)
    await pdf.delete()


async def extract_text(pdf_id: str) -> str:
"""Retorna el texto extraído de un PDF. Lanza excepción si no existe."""
    pdf = await get_pdf_or_raise(pdf_id)
    return pdf.extracted_text or ""
