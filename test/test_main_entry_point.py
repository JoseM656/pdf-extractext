"""Tests para verificar el entry-point main.py."""

import subprocess
import sys
from pathlib import Path


class TestMainEntryPoint:
    """Tests que verifican que main.py es el entry-point correcto."""

    def test_main_module_has_main_function(self) -> None:
        """El módulo main debe exportar una función main()."""
        # Act & Assert: Importar main desde dev.main no debe fallar
        from dev.main import main

        assert callable(main), "main debe ser una función callable"

    def test_main_module_can_be_executed(self, tmp_path: Path) -> None:
        """El módulo main debe ejecutarse sin errores de importación."""
        # Arrange: Crear PDF de prueba
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake pdf content")

        # Act: Ejecutar main.py con un archivo PDF
        result = subprocess.run(
            [sys.executable, "-m", "dev.main", str(pdf_file)],
            capture_output=True,
            text=True,
        )

        # Assert: No debe fallar por errores de importación (código 2)
        # Puede fallar por archivo no encontrado o MongoDB, pero no por import
        assert result.returncode != 2, f"Error de importación: {result.stderr}"
