"""Dependencias de FastAPI para inyectar el repositorio de PDFs."""

from fastapi import Request

from dev.repositories.pdf_repository import PdfRepository


def get_repository(request: Request) -> PdfRepository:
    """Retorna el repositorio configurado en la app (Mongo en prod, in-memory en tests)."""
    return request.app.state.pdf_repository
