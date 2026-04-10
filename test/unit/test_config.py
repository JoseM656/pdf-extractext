"""Tests para el módulo de configuración."""

import pytest
from dev.config import settings


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

    def test_settings_database_url_is_defined(self):
        """La aplicación tiene una URL de base de datos configurada."""
        assert settings.DATABASE_URL is not None
        assert "sqlite" in settings.DATABASE_URL.lower()

    def test_settings_upload_dir_is_defined(self):
        """La aplicación tiene un directorio de uploads configurado."""
        assert settings.UPLOAD_DIR is not None
        assert settings.UPLOAD_DIR == "./uploads"
