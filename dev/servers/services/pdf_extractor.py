"""Servicio de extracción de texto de PDFs."""

import io
import logging

from pypdf import PdfReader

logging.getLogger("pypdf").setLevel(logging.ERROR)
# pypdf emite warnings en stderr cuando encuentra PDFs con xref malformado
# o encabezados inválidos. Esos casos ya están cubiertos por nuestra validación
# de magic bytes en pdf_validator.py. Silenciamos el logger de pypdf para no
# ensuciar los logs del servidor con mensajes que no aportan información accionable.


class PdfExtractionError(Exception):
    """Se lanza cuando el PDF está corrupto o no se puede leer (fallo real)."""


class EmptyPdfError(Exception):
    """Se lanza cuando el PDF es válido pero no contiene texto extraíble."""


class PdfExtractor:
    """Extrae texto de archivos PDF desde contenido en memoria."""

    def extract_text(self, content: bytes) -> str:
        """Extrae todo el texto de un PDF.

        Args:
            content: Contenido binario del PDF (bytes).

        Returns:
            String con el contenido textual del PDF.

        Raises:
            PdfExtractionError: Si el PDF está corrupto o no se puede leer.
            EmptyPdfError: Si el PDF es válido pero no contiene texto.
        """
        try:
            file_like = io.BytesIO(content)
            reader = PdfReader(file_like)
            text_parts = []

            for page in reader.pages:
                page_text = page.extract_text(extraction_mode="layout")
                if page_text:
                    text_parts.append(page_text)

            text = "\n".join(text_parts)
        except Exception as e:
            raise PdfExtractionError(
                "No se pudo extraer el texto del PDF: archivo corrupto o ilegible."
            ) from e

        if not text.strip():
            raise EmptyPdfError("El PDF no contiene texto extraíble.")

        return text
