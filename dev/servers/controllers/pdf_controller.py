"""Lógica de negocio para gestión de documentos PDF — capa de controladores."""

from dev.models.pdf_document import Pdf


async def create_pdf(
    title: str,
    description: str | None,
    size: int,
    extracted_text: str | None = None,
    checksum: str | None = None,
) -> Pdf:
    """Crea y persiste un documento PDF en la base de datos.

    Args:
        title: Título del documento.
        description: Descripción opcional.
        size: Tamaño del archivo en bytes.
        extracted_text: Texto ya extraído del PDF. Se persiste junto al documento
            para no requerir el archivo original en lecturas posteriores.
        checksum: Hash SHA-256 del contenido binario. Se usa para detectar duplicados.

    Returns:
        El documento Pdf recién creado y persistido.
    """
    pdf = Pdf(
        title=title,
        description=description,
        size=size,
        extracted_text=extracted_text,
        checksum=checksum,
    )
    await pdf.insert()
    return pdf


async def get_pdf_by_checksum(checksum: str) -> Pdf | None:
    """Busca un PDF por su checksum SHA-256.

    Se usa para detectar duplicados antes de persistir un nuevo documento.
    Si retorna un documento, significa que el contenido ya fue subido anteriormente.

    Args:
        checksum: Hash SHA-256 del contenido binario a buscar.

    Returns:
        El documento Pdf existente, o None si no hay duplicado.
    """
    return await Pdf.find_one(Pdf.checksum == checksum)


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
    """Elimina un PDF de la base de datos.

    Como los archivos ya no se persisten en disco, solo se elimina
    el documento de MongoDB.

    Args:
        pdf_id: Identificador único del documento a eliminar.

    Raises:
        ValueError: Si no existe un PDF con ese ID.
    """
    pdf = await Pdf.get(pdf_id)
    if pdf is None:
        raise ValueError(f"PDF con id '{pdf_id}' no encontrado")

    # Solo eliminamos el registro de la base de datos.
    # No hay archivo físico que borrar porque el procesamiento es en memoria.
    await pdf.delete()


async def extract_text(pdf_id: str) -> dict:
    """Retorna el texto extraído de un PDF desde la base de datos.

    El texto fue extraído y persistido en el momento del upload,
    por lo que esta operación es una simple lectura de MongoDB.
    No requiere acceso al archivo original.

    Args:
        pdf_id: Identificador único del documento.

    Returns:
        Diccionario con 'pdf_id' y 'text' con el texto extraído.

    Raises:
        ValueError: Si no existe un PDF con ese ID.
    """
    pdf = await Pdf.get(pdf_id)
    if pdf is None:
        raise ValueError(f"PDF con id '{pdf_id}' no encontrado")

    return {
        "pdf_id": pdf_id,
        "text": pdf.extracted_text or "",
    }