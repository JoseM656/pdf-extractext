"""Tests para el módulo de configuración."""

import pytest
from dev.servers.config import settings


class TestConfig:
    """Tests para verificar la configuración de la aplicación."""

    def test_settings_app_name_is_defined(self):
        """La aplicación tiene un nombre configurado."""
        assert settings.APP_NAME is not None
        assert settings.APP_NAME == "PDF Manager"

    def test_settings_version_is_defined(self):
        """La aplicación tiene una versión configurada."""
        assert settings.VERSION is not None
        assert settings.VERSION == "1.0.0"

    def test_settings_mongo_uri_is_defined(self):
        """La aplicación tiene una URI de MongoDB configurada."""
        assert settings.MONGO_URI is not None
        assert "mongodb" in settings.MONGO_URI.lower()

    def test_settings_mongo_db_name_is_defined(self):
        """La aplicación tiene un nombre de base de datos configurado."""
        assert settings.MONGO_DB_NAME is not None
        assert settings.MONGO_DB_NAME == "pdf_manager"

    def test_settings_upload_dir_is_defined(self):
        """La aplicación tiene un directorio de uploads configurado."""
        assert settings.UPLOAD_DIR is not None
        assert settings.UPLOAD_DIR == "./uploads"