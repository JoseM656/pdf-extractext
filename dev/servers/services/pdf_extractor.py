"""Servicio de extracción de texto de PDFs."""

import io
from pathlib import Path
from PyPDF import PdfReader

logging.getLogger("pypdf").setLevel(logging.ERROR)
# pypdf emite warnings en stderr cuando encuentra PDFs con xref malformado
# o encabezados inválidos. Esos casos ya están cubiertos por nuestra validación
# de magic bytes en pdf_validator.py. Silenciamos el logger de pypdf para no
# ensuciar los logs del servidor con mensajes que no aportan información accionable.


class PdfExtractor:
    """Extrae texto de archivos PDF.

    Acepta tanto rutas en disco (Path) como contenido en memoria (bytes),
    para poder procesar PDFs sin necesidad de escribirlos temporalmente a disco.
    """

    def extract_text(self, source: Path | bytes) -> str:
        """Extrae todo el texto de un PDF.

        Args:
            source: Ruta al archivo PDF (Path) o contenido binario del PDF (bytes).

        Returns:
            String con el contenido textual del PDF.
            Retorna string vacío si no hay texto o hay error.
        """
        try:
            # Si recibimos bytes, los envolvemos en BytesIO para que PyPDF2
            # pueda leerlos como si fuera un archivo, sin tocar el disco.
            if isinstance(source, bytes):
                file_like = io.BytesIO(source)
            else:
                file_like = str(source)

            reader = PdfReader(file_like)
            text_parts = []

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

            return "\n".join(text_parts)
        except Exception:
            return ""