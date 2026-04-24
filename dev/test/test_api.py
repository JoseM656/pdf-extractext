"""Tests de integración para los endpoints de la API FastAPI."""

import io
import pytest
from fastapi.testclient import TestClient


class TestCreatePdfEndpoint:
    """Tests para el endpoint POST /api/pdfs."""

    def test_user_can_upload_valid_pdf(
        self, client: TestClient, sample_pdf_bytes: bytes
    ):
        response = client.post(
            "/api/pdfs",
            files={
                "file": (
                    "document.pdf",
                    io.BytesIO(sample_pdf_bytes),
                    "application/pdf",
                )
            },
            data={"title": "My Document", "description": "Test description"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "My Document"
        assert data["description"] == "Test description"
        assert data["id"] is not None
        assert data["size"] > 0
        assert data["created_at"] is not None

    def test_system_rejects_non_pdf_files(self, client: TestClient):
        txt_content = b"This is not a PDF file"
        response = client.post(
            "/api/pdfs",
            files={"file": ("document.txt", io.BytesIO(txt_content), "text/plain")},
            data={"title": "My Document"},
        )

        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]

    def test_pdf_uses_filename_as_title_when_title_empty(
        self, client: TestClient, sample_pdf_bytes: bytes
    ):
        """El PDF usa el nombre del archivo como título cuando no se da uno"""
        response = client.post(
            "/api/pdfs",
            files={
                "file": (
                    "uploaded_doc.pdf",
                    io.BytesIO(sample_pdf_bytes),
                    "application/pdf",
                )
            },
            data={"title": ""},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "uploaded_doc.pdf"

    def test_pdf_uses_provided_title_when_given(
        self, client: TestClient, sample_pdf_bytes: bytes
    ):
        response = client.post(
            "/api/pdfs",
            files={
                "file": (
                    "uploaded_doc.pdf",
                    io.BytesIO(sample_pdf_bytes),
                    "application/pdf",
                )
            },
            data={"title": "Custom Title"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Custom Title"


class TestListPdfsEndpoint:
    """Tests para el endpoint GET /api/pdfs."""

    def test_returns_empty_list_when_no_pdfs_exist(self, client: TestClient):
        """Devuelve lista vacía cuando no existen PDFs"""
        response = client.get("/api/pdfs")

        assert response.status_code == 200
        assert response.json() == []

    def test_returns_pdfs_ordered_by_creation_date(
        self, client: TestClient, sample_pdf_bytes: bytes
    ):
        """Devuelve PDFs ordenados por fecha"""
        client.post(
            "/api/pdfs",
            files={"file": ("first.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")},
            data={"title": "First PDF"},
        )
        client.post(
            "/api/pdfs",
            files={"file": ("second.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")},
            data={"title": "Second PDF"},
        )

        response = client.get("/api/pdfs")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Second PDF"
        assert data[1]["title"] == "First PDF"


class TestGetPdfEndpoint:
    """Tests para el endpoint GET"""

    def test_returns_pdf_when_it_exists(
        self, client: TestClient, sample_pdf_bytes: bytes
    ):
        """Retorna el PDF cuando existe."""
        create_response = client.post(
            "/api/pdfs",
            files={"file": ("doc.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")},
            data={"title": "My Document"},
        )
        pdf_id = create_response.json()["id"]

        response = client.get(f"/api/pdfs/{pdf_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pdf_id
        assert data["title"] == "My Document"

    def test_returns_404_when_pdf_not_found(self, client: TestClient):
        """Retorna 404 cuando el PDF no existe."""
        response = client.get("/api/pdfs/000000000000000000000000")

        assert response.status_code == 404
        assert "Not found" in response.json()["detail"]


class TestDeletePdfEndpoint:
    """Tests para el endpoint DELETE"""

    def test_deletes_pdf_when_it_exists(
        self, client: TestClient, sample_pdf_bytes: bytes
    ):
        create_response = client.post(
            "/api/pdfs",
            files={"file": ("to_delete.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")},
            data={"title": "To Delete"},
        )
        pdf_id = create_response.json()["id"]

        response = client.delete(f"/api/pdfs/{pdf_id}")
        assert response.status_code == 204

        get_response = client.get(f"/api/pdfs/{pdf_id}")
        assert get_response.status_code == 404

    def test_returns_404_when_deleting_nonexistent_pdf(self, client: TestClient):
        """Devuelve 404 cuando se intenta eliminar un PDF que no existe"""
        response = client.delete("/api/pdfs/000000000000000000000000")

        assert response.status_code == 404
        assert "Not found" in response.json()["detail"]


class TestExtractTextEndpoint:
    """Tests para el endpoint GET /api/pdfs/{pdf_id}/text."""

    def test_extracts_text_from_existing_pdf(
        self, client: TestClient, sample_pdf_bytes: bytes
    ):
        """Extrae texto de un PDF existente"""
        create_response = client.post(
            "/api/pdfs",
            files={"file": ("text_doc.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")},
            data={"title": "Text Document"},
        )
        pdf_id = create_response.json()["id"]

        response = client.get(f"/api/pdfs/{pdf_id}/text")

        assert response.status_code == 200
        data = response.json()
        assert data["pdf_id"] == pdf_id
        assert "text" in data

    def test_returns_404_when_extracting_from_nonexistent_pdf(self, client: TestClient):
        """Devuelve 404 cuando se extrae texto de un PDF que no existe"""
        response = client.get("/api/pdfs/000000000000000000000000/text")

        assert response.status_code == 404
        assert "Not found" in response.json()["detail"]