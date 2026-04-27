"""Tests para el PdfExtractor controller."""

import tempfile
from pathlib import Path

import pytest

from dev.servers.services.pdf_extractor import PdfExtractor


class TestPdfExtractor:
    """Tests que verifican la extracción de texto de PDFs."""

    def test_extract_text_from_valid_pdf(self) -> None:
        """Debe extraer texto de un PDF válido."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir) / "sample.pdf"
            pdf_path.write_bytes(
                b"%PDF-1.4\n"
                b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
                b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
                b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                b"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> "
                b"/Contents 4 0 R >>\nendobj\n"
                b"4 0 obj\n<< /Length 50 >>\nstream\n"
                b"BT /F1 12 Tf 100 700 Td (Hola Mundo desde el PDF) Tj ET\n"
                b"endstream\nendobj\n"
                b"xref\n0 5\n"
                b"0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n"
                b"0000000115 00000 n \n0000000294 00000 n \n"
                b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n400\n%%EOF\n"
            )

            extractor = PdfExtractor()
            text = extractor.extract_text(pdf_path)

            assert isinstance(text, str), "El resultado debe ser un string"

    def test_extract_text_returns_content(self) -> None:
        """La extracción debe devolver el contenido textual del PDF."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir) / "document.pdf"
            pdf_path.write_bytes(
                b"%PDF-1.4\n"
                b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
                b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
                b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                b"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> "
                b"/Contents 4 0 R >> endobj\n"
                b"4 0 obj << /Length 55 >> stream\n"
                b"BT /F1 12 Tf 100 700 Td (Este es un documento de prueba) Tj ET\n"
                b"endstream endobj\n"
                b"xref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n"
                b"trailer << /Size 5 /Root 1 0 R >>\nstartxref\n0\n%%EOF\n"
            )

            extractor = PdfExtractor()
            text = extractor.extract_text(pdf_path)

            assert isinstance(text, str), "El resultado debe ser un string"

    def test_extract_text_from_bytes(self) -> None:
        """Debe extraer texto cuando se pasan bytes directamente (sin Path).

        Este caso cubre el flujo en memoria introducido en la issue #14.
        """
        pdf_bytes = (
            b"%PDF-1.4\n"
            b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n"
            b"trailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n0\n%%EOF\n"
        )

        extractor = PdfExtractor()
        text = extractor.extract_text(pdf_bytes)

        assert isinstance(text, str), "El resultado debe ser un string al recibir bytes"