from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "PDF Manager"
    VERSION: str = "1.0.0"

    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "pdf_manager"
    UPLOAD_DIR: str = "./uploads"

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()