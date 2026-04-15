from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "PDF Manager"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./pdf_manager.db"
    UPLOAD_DIR: str = "./uploads"

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
