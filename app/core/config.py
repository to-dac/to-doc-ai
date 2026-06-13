from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "to-dac-backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    ANTHROPIC_API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
