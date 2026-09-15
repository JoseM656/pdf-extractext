"""Lógica de negocio para operaciones sobre PDFs.

Este módulo contiene la lógica pura sin conocimiento de HTTP ni de la
tecnología de persistencia concreta: opera contra el puerto `PdfRepository`,
que recibe como parámetro. Es stateless y reutilizable tanto desde la API
REST como desde un CLI.
"""

from dev.models.pdf_document import PdfDocument
from dev.repositories.pdf_repository import PdfRepository
from dev.servers.services.pdf_extractor import PdfExtractor
from dev.servers.services.pdf_validator import (
    DuplicatePdfError,
    PdfNotFoundError,
    calculate_checksum,
    validate_pdf_bytes,
)


async def get_pdf(repository: PdfRepository, pdf_id: str) -> PdfDocument:
    """Obtiene un PDF por ID o lanza PdfNotFoundError si no existe.

    Este es el único punto de traducción de "PDF no encontrado".
    Todos los métodos que consultan por ID usan este helper.
    """
    pdf = await repository.get_by_id(pdf_id)
    if pdf is None:
        raise PdfNotFoundError(f"No existe un PDF con ID {pdf_id}")
    return pdf


async def get_pdf_by_checksum(
    repository: PdfRepository, checksum: str
) -> PdfDocument | None:
    """Retorna un PDF existente si su checksum coincide, None en caso contrario."""
    return await repository.get_by_checksum(checksum)


async def create_pdf(
    repository: PdfRepository,
    title: str,
    description: str | None,
    size: int,
    extracted_text: str | None,
    checksum: str,
) -> PdfDocument:
    """Crea y persiste un documento PDF a partir de datos ya validados y extraídos."""
    pdf = PdfDocument(
        title=title,
        description=description,
        size=size,
        extracted_text=extracted_text,
        checksum=checksum,
    )
    return await repository.save(pdf)


async def submit_pdf(
    repository: PdfRepository,
    content: bytes,
    filename: str,
    title: str | None,
    description: str | None,
) -> PdfDocument:
    """Orquesta el flujo completo de subida de un PDF."""

    validate_pdf_bytes(content, filename)
 
    checksum = calculate_checksum(content)
 
    existing = await get_pdf_by_checksum(repository, checksum)
    if existing is not None:
        raise DuplicatePdfError(existing_id=str(existing.id))
 
    extracted_text = PdfExtractor().extract_text(content)
 
    return await create_pdf(
        repository,
        title=title or filename,
        description=description,
        size=len(content),
        extracted_text=extracted_text,
        checksum=checksum,
    )

async def list_pdfs(repository: PdfRepository) -> list[PdfDocument]:
    """Retorna todos los PDFs ordenados por fecha de creación descendente."""
    return await repository.list_all()


async def delete_pdf(repository: PdfRepository, pdf_id: str) -> None:
    """Elimina un PDF existente. Lanza excepción si no existe."""
    await get_pdf(repository, pdf_id)
    await repository.delete(pdf_id)


async def extract_text(repository: PdfRepository, pdf_id: str) -> dict:
    """Retorna el texto extraído de un PDF. Lanza excepción si no existe."""
    pdf = await get_pdf(repository, pdf_id)
    return {"pdf_id": pdf_id, "text": pdf.extracted_text or ""}
