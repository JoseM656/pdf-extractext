"""
CLI entry-point para fast-pdf.

Uso: fast-pdf archivo.pdf
"""

import argparse
import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from dev.config import settings
from dev.controllers import PdfExtractor


def _is_pdf_file(file_path: Path) -> bool:
    """Verifica si un archivo tiene extensión PDF."""
    return file_path.suffix.lower() == ".pdf"


async def save_pdf_to_mongodb(pdf_path: Path) -> str | None:
    """Guarda la información del PDF en MongoDB.

    Args:
        pdf_path: Ruta al archivo PDF.

    Returns:
        ID del documento insertado, o None si falló la conexión.
    """
    try:
        client = AsyncIOMotorClient(settings.MONGO_URI)
        db = client[settings.MONGO_DB_NAME]
        pdfs_collection = db["pdfs"]

        pdf_document = {
            "filename": pdf_path.name,
            "path": str(pdf_path),
            "size": pdf_path.stat().st_size,
            "created_at": datetime.now(timezone.utc),
        }

        result = await pdfs_collection.insert_one(pdf_document)
        client.close()

        return str(result.inserted_id)
    except (ConnectionFailure, ServerSelectionTimeoutError):
        return None


async def process_pdf(pdf_path: Path) -> Path:
    """Procesa un archivo PDF y genera un archivo .txt.

    Args:
        pdf_path: Ruta al archivo PDF.

    Returns:
        Ruta al archivo .txt generado.
    """
    await save_pdf_to_mongodb(pdf_path)

    # Extraer texto usando el controller
    extractor = PdfExtractor()
    text = extractor.extract_text(pdf_path)

    output_path = pdf_path.with_suffix(".txt")
    output_path.write_text(text)

    return output_path


def _validate_pdf_path(pdf_path: Path) -> str | None:
    """Valida que la ruta sea un PDF válido.

    Args:
        pdf_path: Ruta a validar.

    Returns:
        Mensaje de error, o None si es válido.
    """
    if not pdf_path.exists():
        return f"El archivo '{pdf_path}' no existe"
    if not _is_pdf_file(pdf_path):
        return f"El archivo '{pdf_path}' no es un PDF"
    return None


def _parse_arguments() -> Path:
    """Parsea los argumentos de línea de comandos.

    Returns:
        Ruta al archivo PDF.
    """
    parser = argparse.ArgumentParser(
        prog="fast-pdf",
        description="Convierte archivos PDF a texto",
    )
    parser.add_argument(
        "pdf_file",
        type=str,
        help="Ruta al archivo PDF a procesar",
    )

    args = parser.parse_args()
    return Path(args.pdf_file)


def main() -> int:
    """Entry point del CLI."""
    pdf_path = _parse_arguments()

    validation_error = _validate_pdf_path(pdf_path)
    if validation_error:
        print(f"Error: {validation_error}", file=sys.stderr)
        return 1

    try:
        output_path = asyncio.run(process_pdf(pdf_path))
        print(f"PDF procesado y guardado. Archivo de salida: {output_path}")
        return 0
    except Exception as e:
        print(f"Error al procesar PDF: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
