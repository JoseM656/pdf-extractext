"""Tests para el servicio de extracción de texto de PDFs."""

import pytest

from dev.servers.services.pdf_extractor import (
    EmptyPdfError,
    PdfExtractionError,
    PdfExtractor,
)

_TEXT_STREAM = b"BT /F1 12 Tf 100 700 Td (Hola Mundo desde el PDF) Tj ET"


def _pdf_bytes(content_stream: bytes = b"") -> bytes:
    """Construye un PDF válido de una página cuyo content stream es `content_stream`.

    Un content stream vacío produce un PDF válido sin texto extraíble.
    """
    header = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> "
        b"/Contents 4 0 R >>\nendobj\n"
        b"4 0 obj\n<< /Length " + str(len(content_stream)).encode() + b" >>\nstream\n"
    )
    return (
        header
        + content_stream
        + b"\nendstream\nendobj\n"
        b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n0\n%%EOF\n"
    )


class TestPdfExtractor:
    """Tests que verifican la extracción de texto de PDFs."""

    def test_extract_text_from_valid_pdf(self) -> None:
        """Debe extraer el texto de un PDF válido con contenido."""
        extractor = PdfExtractor()
        text = extractor.extract_text(_pdf_bytes(_TEXT_STREAM))

        assert text == "Hola Mundo desde el PDF"

    def test_extract_text_raises_for_empty_pdf(self) -> None:
        """Un PDF válido sin texto debe lanzar EmptyPdfError (no guardarse)."""
        extractor = PdfExtractor()

        with pytest.raises(EmptyPdfError):
            extractor.extract_text(_pdf_bytes())

    def test_extract_text_raises_for_corrupt_pdf(self) -> None:
        """Un PDF corrupto o ilegible debe lanzar PdfExtractionError."""
        extractor = PdfExtractor()

        with pytest.raises(PdfExtractionError):
            extractor.extract_text(b"contenido invalido que no es un PDF")
