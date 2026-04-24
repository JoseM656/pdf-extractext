"""Controller para extracción de texto de PDFs."""

from pathlib import Path

from PyPDF2 import PdfReader


class PdfExtractor:
    """Extrae texto de archivos PDF.

    Esta clase encapsula la lógica de extracción de texto
    usando pypdf2 como motor de extracción.
    """

    def extract_text(self, pdf_path: Path) -> str:
        """Extrae todo el texto de un archivo PDF.

        Args:
            pdf_path: Ruta al archivo PDF.

        Returns:
            String con el contenido textual del PDF.
            Retorna string vacío si no hay texto o hay error.
        """
        try:
            reader = PdfReader(str(pdf_path))
            text_parts = []

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

            return "\n".join(text_parts)
        except Exception:
            return ""
