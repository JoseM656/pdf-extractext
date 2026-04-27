"""Tests para el modelo Pdf (documento Beanie/MongoDB)."""

import pytest
from datetime import datetime
from dev.models.pdf_document import Pdf


class TestPdfDocument:
    """Tests para el documento Pdf de MongoDB."""

    def test_pdf_can_be_instantiated_with_valid_data(self):
        """Un PDF puede ser instanciado con datos válidos."""
        pdf = Pdf(
            title="Test PDF",
            description="Test description",
            path="/uploads/test.pdf",
            size=1024,
        )

        assert pdf.title == "Test PDF"
        assert pdf.description == "Test description"
        assert pdf.path == "/uploads/test.pdf"
        assert pdf.size == 1024

    def test_pdf_has_auto_generated_created_at(self):
        """El campo created_at se asigna automáticamente al instanciar un PDF."""
        before_creation = datetime.utcnow()

        pdf = Pdf(title="Test PDF", path="/uploads/test.pdf", size=1024)

        assert pdf.created_at is not None
        assert pdf.created_at >= before_creation

    def test_pdf_description_is_optional(self):
        """El campo description es opcional y puede ser None."""
        pdf = Pdf(title="Test PDF", path="/uploads/test.pdf", size=1024)

        assert pdf.description is None

    def test_pdf_collection_name_is_pdfs(self):
        """El documento se persiste en la colección 'pdfs'."""
        assert Pdf.Settings.name == "pdfs"

    def test_pdf_title_is_required(self):
        """El campo title es obligatorio."""
        with pytest.raises(Exception):
            Pdf(path="/uploads/test.pdf", size=1024)

    def test_pdf_path_is_required(self):
        """El campo path es obligatorio."""
        with pytest.raises(Exception):
            Pdf(title="Test PDF", size=1024)

    def test_pdf_size_is_required(self):
        """El campo size es obligatorio."""
        with pytest.raises(Exception):
            Pdf(title="Test PDF", path="/uploads/test.pdf")

    # --- Tests para campos agregados en issues #15 y #12 ---

    def test_pdf_extracted_text_is_optional(self):
        """El campo extracted_text es opcional y por defecto None."""
        pdf = Pdf(title="Test PDF", path="/uploads/test.pdf", size=1024)

        assert pdf.extracted_text is None

    def test_pdf_extracted_text_can_be_set(self):
        """El campo extracted_text puede almacenar texto extraído."""
        pdf = Pdf(
            title="Test PDF",
            path="/uploads/test.pdf",
            size=1024,
            extracted_text="Contenido del PDF extraído",
        )

        assert pdf.extracted_text == "Contenido del PDF extraído"

    def test_pdf_checksum_is_optional(self):
        """El campo checksum es opcional y por defecto None."""
        pdf = Pdf(title="Test PDF", path="/uploads/test.pdf", size=1024)

        assert pdf.checksum is None

    def test_pdf_checksum_can_be_set(self):
        """El campo checksum puede almacenar un hash SHA-256."""
        sha256_hash = "a" * 64  # SHA-256 produce 64 caracteres hexadecimales
        pdf = Pdf(
            title="Test PDF",
            path="/uploads/test.pdf",
            size=1024,
            checksum=sha256_hash,
        )

        assert pdf.checksum == sha256_hash
        assert len(pdf.checksum) == 64