from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./docuquest.db"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "unsafe-development-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    max_upload_size_mb: int = 20
    storage_path: Path = Path("./data/uploads")
    ocr_provider: str = "tesseract"
    llm_provider: str = "local"
    llm_api_key: str | None = None
    celery_eager: bool = False
    ocr_min_confidence: float = 0.45
    # A short option-continuation page still contains reliable native text.
    native_text_min_chars: int = 10
    confidence_success_threshold: float = 0.85
    confidence_partial_threshold: float = 0.60
    ocr_upscale_factor: int = 2
    host: str = "0.0.0.0"
    port: int = 8000
settings = Settings()
