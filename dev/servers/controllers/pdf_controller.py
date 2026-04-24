from dev.servers.models.pdf_document import Pdf


async def create_pdf(title: str, description: str | None, path: str, size: int) -> Pdf:
    """Crea y persiste un documento PDF."""
    raise NotImplementedError


async def list_pdfs() -> list[Pdf]:
    """Retorna todos los PDFs ordenados por fecha de creación descendente."""
    raise NotImplementedError


async def get_pdf(pdf_id: str) -> Pdf:
    """Retorna un PDF por su ID. Lanza excepción si no existe."""
    raise NotImplementedError


async def delete_pdf(pdf_id: str) -> None:
    """Elimina un PDF y su archivo físico. Lanza excepción si no existe."""
    raise NotImplementedError


async def extract_text(pdf_id: str) -> dict:
    """Extrae el texto de un PDF existente."""
    raise NotImplementedError