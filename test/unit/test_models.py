"""Tests para los modelos de SQLAlchemy."""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from dev.models import Base, Pdf


class TestPdfModel:
    """Tests para el modelo Pdf."""

    @pytest.fixture(scope="function")
    def db_session(self):
        """Proporciona una sesión de base de datos en memoria."""
        engine = create_engine(
            "sqlite:///:memory:", connect_args={"check_same_thread": False}
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
            Base.metadata.drop_all(bind=engine)

    def test_pdf_can_be_created_with_valid_data(self, db_session: Session):
        """Un PDF puede ser creado con datos válidos."""
        pdf = Pdf(
            title="Test PDF",
            description="Test description",
            path="/uploads/test.pdf",
            size=1024,
        )
        db_session.add(pdf)
        db_session.commit()
        db_session.refresh(pdf)

        assert pdf.id is not None
        assert pdf.title == "Test PDF"
        assert pdf.description == "Test description"
        assert pdf.path == "/uploads/test.pdf"
        assert pdf.size == 1024

    def test_pdf_has_auto_generated_created_at(self, db_session: Session):
        """El campo created_at se asigna automáticamente al crear un PDF."""
        before_creation = datetime.utcnow()

        pdf = Pdf(title="Test PDF", path="/uploads/test.pdf", size=1024)
        db_session.add(pdf)
        db_session.commit()
        db_session.refresh(pdf)

        assert pdf.created_at is not None
        assert pdf.created_at >= before_creation

    def test_pdf_description_can_be_null(self, db_session: Session):
        """El campo description puede ser nulo."""
        pdf = Pdf(
            title="Test PDF", description=None, path="/uploads/test.pdf", size=1024
        )
        db_session.add(pdf)
        db_session.commit()
        db_session.refresh(pdf)

        assert pdf.description is None

    def test_pdf_title_is_required(self, db_session: Session):
        """El campo title es obligatorio."""
        pdf = Pdf(title=None, path="/uploads/test.pdf", size=1024)
        db_session.add(pdf)

        with pytest.raises(Exception):
            db_session.commit()

    def test_pdf_path_is_required(self, db_session: Session):
        """El campo path es obligatorio."""
        pdf = Pdf(title="Test PDF", path=None, size=1024)
        db_session.add(pdf)

        with pytest.raises(Exception):
            db_session.commit()

    def test_pdf_size_is_required(self, db_session: Session):
        """El campo size es obligatorio."""
        pdf = Pdf(title="Test PDF", path="/uploads/test.pdf", size=None)
        db_session.add(pdf)

        with pytest.raises(Exception):
            db_session.commit()
