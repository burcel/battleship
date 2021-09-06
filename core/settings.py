import secrets

from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME = "Battleship"
    SERVER_IP = "0.0.0.0"
    SERVER_PORT = 8000
    ACCESS_TOKEN_EXPIRE_MINS: int = 60 * 24 * 30  # 30 days
    SECRET_KEY = secrets.token_urlsafe(32)
    SECRET_ALGORITHM = "HS256"

    class Config:
        case_sensitive = True


settings = Settings()
