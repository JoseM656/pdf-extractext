"""Tests de integración para el CLI de fast-pdf.

El CLI ahora actúa como cliente HTTP de la API FastAPI.Estos tests lo ejercitan
por su ÚNICO punto de entrada público: `python -m dev.main <comando> ...`,
lanzado como subprocess real (igual que un usuario lo invocaría como
`fast-pdf <comando>`). No se importan ni se llaman funciones privadas
(`_cmd_upload`, `_cmd_list`, etc.) directamente.
 
Como el subprocess corre en un intérprete de Python completamente aparte,
`unittest.mock.patch` no puede alcanzarlo (el mock vive en el proceso del
test, no en el proceso hijo). En su lugar, se levanta un servidor HTTP real
y mínimo en localhost (ver `fake_api` más abajo) y se apunta `API_BASE_URL`
del subprocess a él, controlando la respuesta que el CLI recibe realmente
por la red — el mismo mecanismo que ya usaba
`test_upload_reports_connection_error_when_server_is_down` para simular un
servidor caído, solo que acá el servidor sí responde.

"""
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Servidor HTTP de prueba: reemplaza el mockeo de httpx en el estilo anterior.
# ---------------------------------------------------------------------------
 
class _ScriptedRequestHandler(BaseHTTPRequestHandler):
    """Devuelve, para cualquier método/ruta, la respuesta que el test dejó
    programada de antemano en `server.scripted_response`.
 
    No reimplementa la API real (no hay rutas, ni Mongo, ni validación) —
    alcanza con responder lo que el test necesita para verificar cómo
    reacciona el CLI a cada código de estado, que es lo mismo que hacían
    los `MagicMock` originales, pero ahora viajando por un socket real.
    """
 
    def _handle(self) -> None:
        # Guarda la request recibida para que el test pueda inspeccionarla
        # (ej. confirmar que el archivo realmente viajó en el body).
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        self.server.last_request = {  # type: ignore[attr-defined]
            "method": self.command,
            "path": self.path,
            "headers": dict(self.headers.items()),
            "body": body,
        }
 
        status, headers, response_body = self.server.scripted_response  # type: ignore[attr-defined]
        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        if response_body:
            self.wfile.write(response_body)
 
    def do_GET(self) -> None:  # noqa: N802 — nombre impuesto por BaseHTTPRequestHandler
        self._handle()
 
    def do_POST(self) -> None:  # noqa: N802
        self._handle()
 
    def do_DELETE(self) -> None:  # noqa: N802
        self._handle()
 
    def log_message(self, format: str, *args: Any) -> None:  # silencia el log por request
        pass
 
 
class _FakeApi:
    """Handle que el fixture `fake_api` entrega a cada test."""
 
    def __init__(self, server: ThreadingHTTPServer) -> None:
        self._server = server
        self.base_url = f"http://127.0.0.1:{server.server_port}"
 
    def set_response(
        self,
        status: int,
        json_body: dict | list | None = None,
        *,
        text: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Programa la respuesta que el servidor va a devolver a la próxima request."""
        hdrs = dict(headers or {})
        if json_body is not None:
            body = json.dumps(json_body).encode("utf-8")
            hdrs.setdefault("Content-Type", "application/json")
        elif text is not None:
            body = text.encode("utf-8")
            hdrs.setdefault("Content-Type", "text/plain")
        else:
            body = b""
        hdrs.setdefault("Content-Length", str(len(body)))
        self._server.scripted_response = (status, hdrs, body)  # type: ignore[attr-defined]
 
    @property
    def last_request(self) -> dict[str, Any] | None:
        """La última request recibida (method, path, headers, body), o None."""
        return getattr(self._server, "last_request", None)
 
 
@pytest.fixture
def fake_api():
    """Levanta un servidor HTTP real en localhost para que el CLI le pegue.
 
    Reemplaza `patch("httpx.post", ...)` / `patch("httpx.get", ...)`, que no
    funcionan contra un subprocess. Cada test programa la respuesta deseada
    con `fake_api.set_response(...)` antes de invocar el CLI.
    """
    server = ThreadingHTTPServer(("127.0.0.1", 0), _ScriptedRequestHandler)
    server.scripted_response = (200, {}, b"")  # type: ignore[attr-defined]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
 
    yield _FakeApi(server)
 
    server.shutdown()
    thread.join(timeout=2)
 
 
def _run_cli(
    *args: str,
    api_base_url: str | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    """Invoca el entry point público del CLI (`python -m dev.main ...`) como
    lo haría un usuario real, y devuelve stdout/stderr/returncode.
    """
    env = {**os.environ}
    if api_base_url is not None:
        env["API_BASE_URL"] = api_base_url
 
    return subprocess.run(
        [sys.executable, "-m", "dev.main", *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
    )
 
 
# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCliSubcommands:
    """Tests que verifican que el CLI reconoce sus subcomandos."""

    def test_cli_requires_a_subcommand(self) -> None:
        """Sin subcomando, el CLI debe salir con error (código 2 de argparse)."""
        result = subprocess.run(
            [sys.executable, "-m", "dev.main"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2, "Debe fallar si no se pasa ningún subcomando"

    def test_cli_upload_requires_pdf_argument(self) -> None:
        """El subcomando upload sin archivo debe salir con código 2."""
        result = subprocess.run(
            [sys.executable, "-m", "dev.main", "upload"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2, "upload sin archivo debe fallar con error de argumentos"

    def test_cli_get_requires_id_argument(self) -> None:
        """El subcomando get sin ID debe salir con código 2."""
        result = subprocess.run(
            [sys.executable, "-m", "dev.main", "get"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2

    def test_cli_delete_requires_id_argument(self) -> None:
        """El subcomando delete sin ID debe salir con código 2."""
        result = subprocess.run(
            [sys.executable, "-m", "dev.main", "delete"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2


class TestUploadCommand:
    """Tests para el subcomando 'upload'."""

    def test_upload_fails_when_file_does_not_exist(self, tmp_path: Path) -> None:
        """upload con un archivo inexistente debe retornar código 1."""
        result = subprocess.run(
            [sys.executable, "-m", "dev.main", "upload", str(tmp_path / "noexiste.pdf")],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "no existe" in result.stderr.lower()

    def test_upload_reports_connection_error_when_server_is_down(self, tmp_path: Path) -> None:
        """Si el servidor no responde, upload debe informar el error claramente."""
        pdf_file = tmp_path / "doc.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 content")

        # Apuntamos a un puerto donde no hay nada corriendo
        result = _run_cli(
            "upload", str(pdf_file),
            api_base_url="http://localhost:19999",
        )

        assert result.returncode == 1
        assert "conectar" in result.stderr.lower() or "connect" in result.stderr.lower()

    def test_upload_sends_file_to_api(self, tmp_path: Path, fake_api) -> None:
        """upload debe enviar el archivo a POST /api/pdfs y mostrar el ID."""
        pdf_file = tmp_path / "documento.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 content")

        fake_api.set_response(200, {
            "id": "abc123",
            "title": "documento",
            "size": 16,
            "created_at": "2026-01-01T00:00:00",
        })
 
        result = _run_cli("upload", str(pdf_file), api_base_url=fake_api.base_url)
 
        assert result.returncode == 0
        assert "abc123" in result.stdout
        assert "documento" in result.stdout
 
        # Confirma que el archivo realmente viajó por la red como multipart,
        # no solo que el CLI mostró el resultado esperado.
        request = fake_api.last_request
        assert request is not None
        assert request["method"] == "POST"
        assert request["headers"]["Content-Type"].startswith("multipart/form-data")
        assert b'filename="documento.pdf"' in request["body"]

    def test_upload_with_info_flag_shows_size_and_date(self, tmp_path: Path, fake_api) -> None:
        """--info debe mostrar tamaño y fecha además del ID."""
        pdf_file = tmp_path / "documento.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 content")

        fake_api.set_response(200, {
            "id": "abc123",
            "title": "documento",
            "size": 1024,
            "created_at": "2026-01-01T00:00:00",
        })
 
        result = _run_cli("upload", str(pdf_file), "--info", api_base_url=fake_api.base_url)
 
        assert result.returncode == 0
        assert "1024" in result.stdout
        assert "2026-01-01" in result.stdout


    def test_upload_shows_duplicate_message_on_409(self, tmp_path: Path, fake_api) -> None:
        """Si el servidor retorna 409, debe mostrar el ID del documento existente."""
        pdf_file = tmp_path / "dup.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 content")

        fake_api.set_response(409, {
            "detail": {
                "message": "Este documento ya fue subido anteriormente.",
                "existing_id": "existing-abc-123",
            }
        })
 
        result = _run_cli("upload", str(pdf_file), api_base_url=fake_api.base_url)
 
        assert result.returncode == 1
        assert "existing-abc-123" in result.stdout
        assert "duplicado" in result.stdout.lower()

        
    def test_upload_shows_validation_error_on_400(self, tmp_path: Path, fake_api) -> None:
        """Si el servidor retorna 400, debe mostrar el mensaje de error de validación."""
        pdf_file = tmp_path / "invalido.pdf"
        pdf_file.write_bytes(b"esto no es un pdf")

        fake_api.set_response(400, {
            "detail": "El archivo 'invalido.pdf' no es un PDF válido."
        })
 
        result = _run_cli("upload", str(pdf_file), api_base_url=fake_api.base_url)
 
        assert result.returncode == 1
        assert "validación" in result.stderr.lower() or "error" in result.stderr.lower()


    def test_upload_shows_error_message_on_422(self, tmp_path: Path, fake_api) -> None:
        """Si el servidor retorna 422 (PDF corrupto o sin texto), debe mostrar el detalle."""
        pdf_file = tmp_path / "vacio.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\ncontenido invalido")

        fake_api.set_response(422, {
            "detail": "El PDF no contiene texto extraíble."
        })
 
        result = _run_cli("upload", str(pdf_file), api_base_url=fake_api.base_url)
 
        assert result.returncode == 1
        assert "no contiene texto" in result.stderr.lower()


class TestListCommand:
    """Tests para el subcomando 'list'."""

    def test_list_shows_empty_message_when_no_pdfs(self, fake_api) -> None:
        """Si no hay PDFs, list debe informarlo claramente."""
        fake_api.set_response(200, [])

        result = _run_cli("list", api_base_url=fake_api.base_url)

        assert result.returncode == 0
        assert "no hay" in result.stdout.lower()


    def test_list_shows_pdf_entries(self, fake_api) -> None:
        """list debe mostrar ID, título, tamaño y fecha de cada PDF."""
        fake_api.set_response(200, [
            {
                "id": "abc123",
                "title": "Mi Documento",
                "size": 2048,
                "created_at": "2026-01-15T10:30:00",
            }
        ])
 
        result = _run_cli("list", api_base_url=fake_api.base_url)
 
        assert result.returncode == 0
        assert "abc123" in result.stdout
        assert "Mi Documento" in result.stdout


class TestGetCommand:
    """Tests para el subcomando 'get'."""

    def test_get_shows_extracted_text(self, fake_api) -> None:
        """get debe imprimir el texto extraído del PDF."""
        fake_api.set_response(200, {
            "pdf_id": "abc123",
            "text": "Contenido del documento PDF.",
        })
 
        result = _run_cli("get", "abc123", api_base_url=fake_api.base_url)
 
        assert result.returncode == 0
        assert "Contenido del documento PDF." in result.stdout


    def test_get_returns_1_when_pdf_not_found(self, fake_api) -> None:
        """get debe retornar código 1 y mensaje de error si el ID no existe."""
        fake_api.set_response(404)
 
        result = _run_cli("get", "id-inexistente", api_base_url=fake_api.base_url)
 
        assert result.returncode == 1
        assert "no existe" in result.stderr.lower()


class TestDeleteCommand:
    """Tests para el subcomando 'delete'."""

    def test_delete_confirms_deletion(self, fake_api) -> None:
        """delete debe confirmar que el documento fue eliminado."""
        fake_api.set_response(204)
 
        result = _run_cli("delete", "abc123", api_base_url=fake_api.base_url)
 
        assert result.returncode == 0
        assert "eliminado" in result.stdout.lower()


    def test_delete_returns_1_when_pdf_not_found(self, fake_api) -> None:
        """delete debe retornar código 1 si el ID no existe."""
        fake_api.set_response(404)
 
        result = _run_cli("delete", "id-inexistente", api_base_url=fake_api.base_url)
 
        assert result.returncode == 1
            

class TestDownloadCommand:
    """Tests para el subcomando 'download'."""

    def test_download_saves_file_with_default_name(
        self, tmp_path: Path, fake_api
    ) -> None:
        """download guarda el texto en un archivo con el nombre del título."""
        fake_api.set_response(
            200,
            text="Contenido del PDF.",
            headers={"content-disposition": 'attachment; filename="Mi Documento.txt"'},
        )
 
        # Se usa cwd= del subprocess (no os.chdir) para no mutar el directorio
        # de trabajo del proceso de test, que persistiría entre tests.
        result = _run_cli("download", "abc123", api_base_url=fake_api.base_url, cwd=tmp_path)
 
        assert result.returncode == 0
        assert (tmp_path / "Mi Documento.txt").exists()


    def test_download_saves_file_with_custom_name(
        self, tmp_path: Path, fake_api
) -> None:
        """--output permite especificar el nombre del archivo."""
        fake_api.set_response(
            200,
            text="Contenido del PDF.",
            headers={"content-disposition": 'attachment; filename="Mi Documento.txt"'},
        )
 
        output_file = tmp_path / "mi_archivo.txt"
 
        result = _run_cli(
            "download", "abc123", "--output", str(output_file),
            api_base_url=fake_api.base_url,
        )
 
        assert result.returncode == 0
        assert output_file.exists()
        assert output_file.read_text() == "Contenido del PDF."


    def test_download_returns_1_when_pdf_not_found(self, fake_api) -> None:
        """download retorna código 1 si el ID no existe."""
        fake_api.set_response(404)
 
        result = _run_cli("download", "id-inexistente", api_base_url=fake_api.base_url)
 
        assert result.returncode == 1