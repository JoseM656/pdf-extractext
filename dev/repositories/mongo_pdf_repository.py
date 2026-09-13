"""Adaptador Mongo/Beanie del puerto PdfRepository.

Es el único lugar del proyecto que conoce Beanie/MongoDB. El documento Beanie
`PdfDocumentModel` es un detalle de implementación interno: la lógica de negocio
solo ve `PdfDocument` (entidad de dominio) a través del puerto `PdfRepository`.
"""

from datetime import datetime
from typing import Annotated

from beanie import Document, Indexed, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import Field

from dev.config import settings
from dev.models.pdf_document import PdfDocument
from dev.repositories.pdf_repository import PdfRepository


class PdfDocumentModel(Document):
    """Documento Beanie persistido en la colección 'pdfs'."""

    title: str
    description: str | None = None
    size: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    extracted_text: str | None = None
    checksum: Annotated[str, Indexed(unique=True)] | None = None

    class Settings:
        name = "pdfs"


class MongoPdfRepository:
    """Persistencia de documentos PDF sobre MongoDB vía Beanie."""

    def __init__(self) -> None:
        self._client: AsyncIOMotorClient | None = None

    async def initialize(self) -> None:
        self._client = AsyncIOMotorClient(settings.MONGO_URI)
        await init_beanie(
            database=self._client[settings.MONGO_DB_NAME],
            document_models=[PdfDocumentModel],
        )

    async def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    async def save(self, pdf: PdfDocument) -> PdfDocument:
        model = PdfDocumentModel(**pdf.model_dump(exclude={"id"}))
        await model.insert()
        return self._to_domain(model)

    async def get_by_id(self, pdf_id: str) -> PdfDocument | None:
        model = await PdfDocumentModel.get(pdf_id)
        return self._to_domain(model) if model else None

    async def get_by_checksum(self, checksum: str) -> PdfDocument | None:
        model = await PdfDocumentModel.find_one({"checksum": checksum})
        return self._to_domain(model) if model else None

    async def list_all(self) -> list[PdfDocument]:
        models = await PdfDocumentModel.find().sort("-created_at").to_list()
        return [self._to_domain(model) for model in models]

    async def delete(self, pdf_id: str) -> bool:
        model = await PdfDocumentModel.get(pdf_id)
        if model is None:
            return False
        await model.delete()
        return True

    @staticmethod
    def _to_domain(model: PdfDocumentModel) -> PdfDocument:
        return PdfDocument(
            id=str(model.id),
            title=model.title,
            description=model.description,
            size=model.size,
            created_at=model.created_at,
            extracted_text=model.extracted_text,
            checksum=model.checksum,
        )
