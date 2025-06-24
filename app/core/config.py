# app/core/config.py
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict   # pip install pydantic-settings

class Settings(BaseSettings):
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
    MODEL_DIR:    Path = PROJECT_ROOT / "train_detection"
    DET_WEIGHT:   Path = MODEL_DIR / "best.pt"

    DB_URL: str = "sqlite:///./dispatch.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()   # <-- BẮT BUỘC
