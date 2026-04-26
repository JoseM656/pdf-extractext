"""Lógica de negocio para gestión de documentos PDF — capa de controladores."""

from pathlib import Path

from dev.servers.services.pdf_extractor import PdfExtractor
from dev.models.pdf_document import Pdf


async def create_pdf(title: str, description: str | None, path: str, size: int) -> Pdf:
    """Crea y persiste un documento PDF en la base de datos.

    Args:
        title: Título del documento.
        description: Descripción opcional.
        path: Ruta física donde fue guardado el archivo.
        size: Tamaño del archivo en bytes.

    Returns:
        El documento Pdf recién creado y persistido.
    """
    pdf = Pdf(title=title, description=description, path=path, size=size)
    await pdf.insert()
    return pdf


async def list_pdfs() -> list[Pdf]:
    """Retorna todos los PDFs ordenados por fecha de creación descendente.

    Returns:
        Lista de documentos Pdf. Puede estar vacía.
    """
    return await Pdf.find().sort(-Pdf.created_at).to_list()


async def get_pdf(pdf_id: str) -> Pdf:
    """Retorna un PDF por su ID.

    Args:
        pdf_id: Identificador único del documento.

    Returns:
        El documento Pdf correspondiente.

    Raises:
        ValueError: Si no existe un PDF con ese ID.
    """
    pdf = await Pdf.get(pdf_id)
    if pdf is None:
        raise ValueError(f"PDF con id '{pdf_id}' no encontrado")
    return pdf


async def delete_pdf(pdf_id: str) -> None:
    """Elimina un PDF de la base de datos y su archivo físico.

    Args:
        pdf_id: Identificador único del documento a eliminar.

    Raises:
        ValueError: Si no existe un PDF con ese ID.
    """
    pdf = await Pdf.get(pdf_id)
    if pdf is None:
        raise ValueError(f"PDF con id '{pdf_id}' no encontrado")

    Path(pdf.path).unlink(missing_ok=True)
    await pdf.delete()


async def extract_text(pdf_id: str) -> dict:
    """Extrae el contenido textual de un PDF existente.

    Args:
        pdf_id: Identificador único del documento.

    Returns:
        Diccionario con la clave 'text' conteniendo el texto extraído.

    Raises:
        ValueError: Si no existe un PDF con ese ID.
    """
    pdf = await Pdf.get(pdf_id)
    if pdf is None:
        raise ValueError(f"PDF con id '{pdf_id}' no encontrado")

    extractor = PdfExtractor()
    text = extractor.extract_text(Path(pdf.path))
    return {"text": text}