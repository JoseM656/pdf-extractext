"""Implementación in-memory de PdfRepository, para tests."""

import uuid

from dev.models.pdf_document import PdfDocument
from dev.repositories.pdf_repository import PdfRepository


class InMemoryPdfRepository:
    """Almacena documentos PDF en un dict, sin persistencia externa."""

    def __init__(self) -> None:
        self._pdfs: dict[str, PdfDocument] = {}

    async def initialize(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def save(self, pdf: PdfDocument) -> PdfDocument:
        pdf_id = str(uuid.uuid4())
        pdf.id = pdf_id
        self._pdfs[pdf_id] = pdf
        return pdf

    async def get_by_id(self, pdf_id: str) -> PdfDocument | None:
        return self._pdfs.get(pdf_id)

    async def get_by_checksum(self, checksum: str) -> PdfDocument | None:
        for pdf in self._pdfs.values():
            if pdf.checksum == checksum:
                return pdf
        return None

    async def list_all(self) -> list[PdfDocument]:
        return sorted(self._pdfs.values(), key=lambda pdf: pdf.created_at, reverse=True)

    async def delete(self, pdf_id: str) -> bool:
        return self._pdfs.pop(pdf_id, None) is not None
