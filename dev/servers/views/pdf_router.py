"""Router FastAPI — capa de presentación del servidor (HTTP)."""

import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from dev.config import settings
from dev.servers.controllers import pdf_controller

router = APIRouter(prefix="/api/pdfs", tags=["pdfs"])


class PdfResponse(BaseModel):
    id: str
    title: str
    description: str | None
    size: int
    created_at: str

    class Config:
        from_attributes = True


def _to_response(pdf) -> PdfResponse:
    """Convierte un documento Pdf al esquema de respuesta HTTP."""
    return PdfResponse(
        id=str(pdf.id),
        title=pdf.title,
        description=pdf.description,
        size=pdf.size,
        created_at=pdf.created_at.isoformat(),
    )


@router.post("", response_model=PdfResponse, status_code=200)
async def create_pdf(
    file: UploadFile = File(...),
    title: str = Form(""),
    description: str | None = Form(None),
):
    """Sube un archivo PDF y lo registra en la base de datos."""
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    dest = upload_dir / file.filename
    with dest.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    used_title = title or file.filename
    size = dest.stat().st_size

    pdf = await pdf_controller.create_pdf(
        title=used_title,
        description=description,
        path=str(dest),
        size=size,
    )
    return _to_response(pdf)


@router.get("", response_model=list[PdfResponse])
async def list_pdfs():
    """Retorna todos los PDFs registrados."""
    pdfs = await pdf_controller.list_pdfs()
    return [_to_response(p) for p in pdfs]


@router.get("/{pdf_id}", response_model=PdfResponse)
async def get_pdf(pdf_id: str):
    """Retorna un PDF por su ID."""
    try:
        pdf = await pdf_controller.get_pdf(pdf_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _to_response(pdf)


@router.delete("/{pdf_id}", status_code=204)
async def delete_pdf(pdf_id: str):
    """Elimina un PDF y su archivo físico."""
    try:
        await pdf_controller.delete_pdf(pdf_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{pdf_id}/text")
async def extract_text(pdf_id: str):
    """Extrae y retorna el texto de un PDF."""
    try:
        return await pdf_controller.extract_text(pdf_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))