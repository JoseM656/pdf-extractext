from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pathlib import Path
import uuid
from PyPDF2 import PdfReader

from dev.config import settings
from dev.database import engine, get_db, SessionLocal
from dev.models import Base, Pdf


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    class PdfResponse(BaseModel):
        id: int
        title: str
        description: str | None
        size: int
        created_at: str

        class Config:
            from_attributes = True

    @app.post("/api/pdfs", response_model=PdfResponse)
    def create_pdf(
        file: UploadFile = File(...),
        title: str = Form(""),
        description: str | None = Form(None),
        db: Session = Depends(get_db),
    ):
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files")

        content = file.file.read()
        file_id = str(uuid.uuid4())
        path = upload_dir / f"{file_id}.pdf"
        path.write_bytes(content)

        pdf = Pdf(
            title=title or file.filename,
            description=description,
            path=str(path),
            size=len(content),
        )
        db.add(pdf)
        db.commit()
        db.refresh(pdf)
        return pdf

    @app.get("/api/pdfs", response_model=list[PdfResponse])
    def list_pdfs(db: Session = Depends(get_db)):
        return db.query(Pdf).order_by(Pdf.created_at.desc()).all()

    @app.get("/api/pdfs/{pdf_id}", response_model=PdfResponse)
    def get_pdf(pdf_id: int, db: Session = Depends(get_db)):
        pdf = db.query(Pdf).filter(Pdf.id == pdf_id).first()
        if not pdf:
            raise HTTPException(status_code=404, detail="Not found")
        return pdf

    @app.delete("/api/pdfs/{pdf_id}", status_code=204)
    def delete_pdf(pdf_id: int, db: Session = Depends(get_db)):
        pdf = db.query(Pdf).filter(Pdf.id == pdf_id).first()
        if not pdf:
            raise HTTPException(status_code=404, detail="Not found")
        Path(pdf.path).unlink(missing_ok=True)
        db.delete(pdf)
        db.commit()

    @app.get("/api/pdfs/{pdf_id}/text")
    def extract_text(pdf_id: int, db: Session = Depends(get_db)):
        pdf = db.query(Pdf).filter(Pdf.id == pdf_id).first()
        if not pdf:
            raise HTTPException(status_code=404, detail="Not found")

        reader = PdfReader(pdf.path)
        text = "\n".join(page.extract_text() for page in reader.pages)
        return {"pdf_id": pdf_id, "text": text}

    return app


app = create_app()
