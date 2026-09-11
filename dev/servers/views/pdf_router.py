"""Endpoints HTTP de la API FastAPI.
 
Aquí se define solo la lógica de HTTP: parseo de requests, traducciones a respuestas,
códigos de estado. La lógica de negocio puro está en los controllers.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from dev.servers.controllers import pdf_controller
from dev.servers.services.pdf_validator import PdfNotFoundError, PdfValidationError

router = APIRouter(prefix="/api/pdfs", tags=["pdfs"])


class PdfResponse(BaseModel):
    id: str
    title: str
    description: str | None
    size: int
    created_at: str

    class Config:
        from_attributes = True


@router.post("", response_model=PdfResponse, status_code=200)
async def create_pdf(
    file: UploadFile = File(...),
    title: str = Form(""),
    description: str | None = Form(None),
):
    """Sube un PDF nuevo a la base de datos."""
    try:
        # Lógica de negocio
        pdf = await pdf_controller.create_pdf(
            title=title or file.filename,
            description=description,
            size=len(file.file.getvalue()),
        )
        return pdf
    except PdfValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[PdfResponse])
async def list_pdfs():
    """Lista todos los PDFs."""
    return await pdf_controller.list_pdfs()


@router.get("/{pdf_id}", response_model=PdfResponse)
async def get_pdf(pdf_id: str):
    """Retorna un PDF por su ID."""
    try:
        return await pdf_controller.get_pdf_or_raise(pdf_id)
    except PdfNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{pdf_id}", status_code=204)
async def delete_pdf(pdf_id: str):
    """Elimina un PDF de la base de datos."""
    try:
        await pdf_controller.delete_pdf(pdf_id)
    except PdfNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{pdf_id}/text")
async def extract_text(pdf_id: str):
    """Extrae y retorna el texto de un PDF."""
    try:
        text = await pdf_controller.extract_text(pdf_id)
        return {"pdf_id": pdf_id, "text": text}
    except PdfNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
 