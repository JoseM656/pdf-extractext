"""Puerto de persistencia para documentos PDF.

Define la interfaz que el dominio usa para guardar y consultar PDFs,
desacoplándolo de la tecnología concreta (MongoDB, in-memory, etc.).
"""

from typing import Protocol

from dev.models.pdf_document import PdfDocument


class PdfRepository(Protocol):
    """Contrato de persistencia de documentos PDF."""

    async def initialize(self) -> None:
        """Prepara la conexión/estado del repositorio."""
        ...

    async def close(self) -> None:
        """Libera los recursos del repositorio."""
        ...

    async def save(self, pdf: PdfDocument) -> PdfDocument:
        """Persiste un documento y lo retorna con su id asignado."""
        ...

    async def get_by_id(self, pdf_id: str) -> PdfDocument | None:
        """Retorna el documento con el id dado, o None si no existe."""
        ...

    async def get_by_checksum(self, checksum: str) -> PdfDocument | None:
        """Retorna el documento con el checksum dado, o None si no existe."""
        ...

    async def list_all(self) -> list[PdfDocument]:
        """Retorna todos los documentos ordenados por fecha de creación descendente."""
        ...

    async def delete(self, pdf_id: str) -> bool:
        """Elimina el documento con el id dado. Retorna True si existía."""
        ...
