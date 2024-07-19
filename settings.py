"""Module for storing settings for the app."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings class for the app."""

    DB_NAME: str = "postgres"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    class Config:
        env_file = ".env"


settings = Settings()
