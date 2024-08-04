from pydantic_settings import BaseSettings


class ServiceSettings(BaseSettings):
    MAX_IMAGE_SIZE: int = 8 * 1024 * 1024  # in bytes
    ALLOWED_IMAGE_TYPES: str = "png,jpeg,gif,apng,webp"
    PAGINATION_MAX_PER_PAGE: int = 50
    MAX_MEMES_TEXT_LENGTH: int = 256
    DB_TABLE_NAME: str = "Memes"
    MAX_FILE_NAME_LENGTH: int = 36  # (UUID -> str) has length equal 36


class DatabaseSettings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    PGDATA: str
    POSTGRES_PORT: int = 5432


database_settings = DatabaseSettings()
service_settings = ServiceSettings()
