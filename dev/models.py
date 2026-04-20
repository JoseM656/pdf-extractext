from beanie import Document
from datetime import datetime
from pydantic import Field


class Pdf(Document):
    title: str
    description: str | None = None
    path: str
    size: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "pdfs"