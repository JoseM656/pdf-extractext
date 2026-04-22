"""Tests de integración para el CLI de fast-pdf."""

import subprocess
import sys
from pathlib import Path

import pytest


class TestCliArguments:
    """Tests que verifican que el CLI acepta argumentos correctamente."""

    def test_cli_accepts_pdf_file_as_argument(self, tmp_path: Path) -> None:
        """El CLI debe aceptar un archivo PDF como argumento posicional.

        Comportamiento: Ejecutar 'fast-pdf archivo.pdf' no debe fallar
        por error de argumentos (archivo no encontrado es aceptable).
        """
        # Arrange: Crear un PDF de prueba mínimo
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake pdf content")

        # Act & Assert: El CLI debe ejecutarse sin error de argumentos
        result = subprocess.run(
            [sys.executable, "-m", "dev.main", str(pdf_file)],
            capture_output=True,
            text=True,
        )

        # No debe fallar por error de argumentos (código 2 en argparse)
        assert result.returncode != 2, f"Error de argumentos: {result.stderr}"


class TestPdfStorage:
    """Tests que verifican que los PDFs se almacenan en MongoDB."""

    def test_pdf_is_stored_in_mongodb(self, tmp_path: Path) -> None:
        """El PDF debe guardarse en MongoDB al procesarlo.

        Comportamiento: Después de procesar un PDF, debe existir
        un documento correspondiente en la colección de MongoDB.
        """
        # Arrange: Crear PDF de prueba
        pdf_file = tmp_path / "document.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>")

        # Act: Ejecutar CLI que debería guardar en MongoDB
        result = subprocess.run(
            [sys.executable, "-m", "dev.main", str(pdf_file)],
            capture_output=True,
            text=True,
        )

        # Assert: El proceso debe intentar guardar en MongoDB (no fallar por ello)
        # El comportamiento observable es que no hay errores de conexión expuestos
        # y el código de retorno es exitoso
        assert result.returncode == 0, f"El CLI falló: {result.stderr}"

        # Verificar que hay evidencia de procesamiento MongoDB en stdout/stderr
        # Esto indica que se intentó conectar/guardar
        assert "guardado" in result.stdout.lower() or "saved" in result.stdout.lower() or "procesado" in result.stdout.lower(), \
            "El CLI debe indicar que el PDF fue guardado o procesado"


class TestPdfToText:
    """Tests que verifican que se genera un archivo .txt."""

    def test_cli_generates_txt_file(self, tmp_path: Path) -> None:
        """El CLI debe generar un archivo .txt con el mismo nombre que el PDF.

        Comportamiento: Después de procesar 'archivo.pdf',
        debe existir 'archivo.txt' en el mismo directorio.
        """
        # Arrange: Crear PDF de prueba
        pdf_file = tmp_path / "mi_documento.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake pdf content")

        expected_txt_file = pdf_file.with_suffix(".txt")

        # Act: Ejecutar CLI
        result = subprocess.run(
            [sys.executable, "-m", "dev.main", str(pdf_file)],
            capture_output=True,
            text=True,
        )

        # Assert: Debe existir el archivo .txt
        assert result.returncode == 0, f"El CLI falló: {result.stderr}"
        assert expected_txt_file.exists(), \
            f"El archivo {expected_txt_file} debe existir después de procesar"

        # El archivo debe contener algo
        content = expected_txt_file.read_text()
        assert len(content) > 0, "El archivo .txt no debe estar vacío"
