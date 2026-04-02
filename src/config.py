from pydantic_settings import BaseSettings

settings = BaseSettings(
    APP_NAME="PDF Manager",
    VERSION="1.0.0",
    DATABASE_URL="sqlite:///./pdf_manager.db",
    UPLOAD_DIR="./uploads",
)
