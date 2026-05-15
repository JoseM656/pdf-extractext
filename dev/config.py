from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "PDF Manager"
    VERSION: str = "1.0.0"

    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "pdf_manager"

    MAX_FILE_SIZE_MB: int = 10
    API_BASE_URL: str = "http://localhost:8000"

    # Esta linea es clave para sobreescribir la configuracion del entorno.
    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()