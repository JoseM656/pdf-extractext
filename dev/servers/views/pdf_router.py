"""Router FastAPI — capa de presentación del servidor (HTTP)."""

import hashlib

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from dev.servers.controllers import pdf_controller
from dev.servers.services.pdf_extractor import PdfExtractor
from dev.servers.services.pdf_validator import PdfValidationError, validate_pdf_bytes
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/api/pdfs", tags=["pdfs"])


class PdfResponse(BaseModel):
    id: str
    title: str
    description: str | None
    size: int
    created_at: str


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
    """Sube un archivo PDF, lo valida, extrae su texto y lo registra en la base de datos.

    El archivo NO se persiste en disco en ningún momento: se lee a memoria,
    se valida, se extrae el texto y solo ese resultado se guarda en MongoDB.
    Retorna HTTP 409 si el contenido del archivo ya fue subido anteriormente.
    """
    # Leer el contenido completo en memoria de una sola vez.
    content: bytes = await file.read()

    # Validar formato real (magic bytes %PDF-) y tamaño máximo.
    try:
        validate_pdf_bytes(content, file.filename or "")
    except PdfValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Calcular el checksum SHA-256 del contenido binario.
    # Es la huella digital del archivo: dos archivos con el mismo hash
    # tienen exactamente el mismo contenido, sin importar el nombre.
    checksum = hashlib.sha256(content).hexdigest()

    # Verificar duplicado antes de cualquier procesamiento costoso.
    # Si el checksum ya existe en la base de datos, el archivo fue subido antes.
    existing = await pdf_controller.get_pdf_by_checksum(checksum)
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Este documento ya fue subido anteriormente.",
                "existing_id": str(existing.id),
            },
        )

    # Extraer el texto mientras los bytes están en memoria.
    extractor = PdfExtractor()
    extracted_text = extractor.extract_text(content)

    used_title = title or file.filename
    size = len(content)

    pdf = await pdf_controller.create_pdf(
        title=used_title,
        description=description,
        size=size,
        extracted_text=extracted_text,
        checksum=checksum,
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
    """Elimina un PDF de la base de datos."""
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
 
    
@router.get("/{pdf_id}/download", response_class=PlainTextResponse)
async def download_text(pdf_id: str):
    """Descarga el texto extraído de un PDF como archivo .txt."""
    try:
        pdf = await pdf_controller.get_pdf(pdf_id)
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