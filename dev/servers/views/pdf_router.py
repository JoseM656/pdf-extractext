from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel

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


@router.post("", response_model=PdfResponse, status_code=200)
async def create_pdf(
    file: UploadFile = File(...),
    title: str = Form(""),
    description: str | None = Form(None),
):
    raise NotImplementedError


@router.get("", response_model=list[PdfResponse])
async def list_pdfs():
    raise NotImplementedError


@router.get("/{pdf_id}", response_model=PdfResponse)
async def get_pdf(pdf_id: str):
    raise NotImplementedError


@router.delete("/{pdf_id}", status_code=204)
async def delete_pdf(pdf_id: str):
    raise NotImplementedError


@router.get("/{pdf_id}/text")
async def extract_text(pdf_id: str):
    raise NotImplementedError