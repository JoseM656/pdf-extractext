"""Router FastAPI — capa de presentación del servidor (HTTP)."""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel

from dev.repositories.pdf_repository import PdfRepository
from dev.servers.controllers import pdf_controller
from dev.servers.dependencies import get_repository
from dev.servers.services.pdf_extractor import (
    EmptyPdfError,
    PdfExtractionError,
)
from dev.servers.services.pdf_validator import (
    DuplicatePdfError,
    PdfValidationError
)
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/api/pdfs", tags=["pdfs"])


class PdfResponse(BaseModel):
    id: str
    title: str
    description: str | None
    size: int
    checksum: str | None
    created_at: str


def _to_response(pdf) -> PdfResponse:
    """Convierte un documento Pdf al esquema de respuesta HTTP."""
    return PdfResponse(
        id=str(pdf.id),
        title=pdf.title,
        description=pdf.description,
        size=pdf.size,
        checksum=pdf.checksum,
        created_at=pdf.created_at.isoformat(),
    )


@router.post("", response_model=PdfResponse, status_code=200)
async def create_pdf(
    repository: PdfRepository = Depends(get_repository),
    file: UploadFile = File(...),
    title: str = Form(""),
    description: str | None = Form(None),
):
    """Sube un archivo PDF, lo valida, extrae su texto y lo registra en la base de datos."""
    # Leer el contenido completo en memoria de una sola vez.
    content: bytes = await file.read()

    # Validar formato real (magic bytes %PDF-) y tamaño máximo.
    try:
        pdf = await pdf_controller.submit_pdf(
            repository,
            content=content,
            filename=file.filename or "",
            title=title,
            description=description,
        )
    except PdfValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DuplicatePdfError as e:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Este documento ya fue subido anteriormente.",
                "existing_id": e.existing_id,
            },
        )
    except (PdfExtractionError, EmptyPdfError) as e:
        raise HTTPException(status_code=422, detail=str(e))
 
    return _to_response(pdf)


@router.get("", response_model=list[PdfResponse])
async def list_pdfs(repository: PdfRepository = Depends(get_repository)):
    """Retorna todos los PDFs registrados."""
    pdfs = await pdf_controller.list_pdfs(repository)
    return [_to_response(p) for p in pdfs]


@router.get("/{pdf_id}", response_model=PdfResponse)
async def get_pdf(
    pdf_id: str, repository: PdfRepository = Depends(get_repository)
):
    """Retorna un PDF por su ID."""
    try:
        pdf = await pdf_controller.get_pdf(repository, pdf_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _to_response(pdf)


@router.delete("/{pdf_id}", status_code=204)
async def delete_pdf(
    pdf_id: str, repository: PdfRepository = Depends(get_repository)
):
    """Elimina un PDF de la base de datos."""
    try:
        await pdf_controller.delete_pdf(repository, pdf_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{pdf_id}/text")
async def extract_text(
    pdf_id: str, repository: PdfRepository = Depends(get_repository)
):
    """Extrae y retorna el texto de un PDF."""
    try:
        return await pdf_controller.extract_text(repository, pdf_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    
@router.get("/{pdf_id}/download", response_class=PlainTextResponse)
async def download_text(
    pdf_id: str, repository: PdfRepository = Depends(get_repository)
):
    """Descarga el texto extraído de un PDF como archivo .txt."""
    try:
        pdf = await pdf_controller.get_pdf(repository, pdf_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    text = pdf.extracted_text or ""
    filename = f"{pdf.title}.txt"

    return PlainTextResponse(
        content=text,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
