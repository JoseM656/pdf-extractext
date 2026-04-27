from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "PDF Manager"
    VERSION: str = "1.0.0"

    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "pdf_manager"
    UPLOAD_DIR: str = "./uploads"

    # Tamaño máximo permitido para archivos PDF (en MB).
    # Configurable vía variable de entorno MAX_FILE_SIZE_MB=20
    MAX_FILE_SIZE_MB: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()