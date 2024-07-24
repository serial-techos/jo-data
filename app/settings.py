"""Module for storing settings for the app."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings class for the app."""

    DB_NAME: str = "postgres"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    CONN_STRING: str = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    PYTHONPATH: str = "."
    MAPBOX_TOKEN: str = ""

    class Config:
        env_file = ".env"
        ignore_extra = True


settings = Settings()
