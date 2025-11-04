"""Набор настроек приложения"""

from datetime import timedelta
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Класс настроек базы данных"""

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def get_db_url(self) -> str:
        """Возвращает URL для подключения к базе данных"""
        return (f"postgresql+asyncpg://{self.DB_USER}:"
                f"{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")


class AuthSettings(BaseSettings):
    """Класс настроек аутентификации"""

    JWT_SECRET_KEY: str
    JWT_COOKIE_ACCESS_NAME: str
    JWT_COOKIE_REFRESH_NAME: str
    JWT_ACCESS_TOKEN_EXPIRES: timedelta
    JWT_REFRESH_TOKEN_EXPIRES: timedelta

    @property
    def JWT_COOKIE_MAX_AGE(self) -> float:  # pylint: disable=invalid-name
        """Возвращает максимальное время жизни куки"""
        return self.JWT_REFRESH_TOKEN_EXPIRES.total_seconds()

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class BotSettings(BaseSettings):
    """Класс настроек бота"""

    BOT_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class RedisSettings(BaseSettings):
    """Класс настроек Redis"""

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    STREAM_FROM_BACKEND: str
    STREAM_TO_BACKEND: str

    def get_redis_url(self) -> str:
        """Собрать URL для подключения к Redis"""
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class MinioSettings(BaseSettings):
    """Класс настроек MinIO"""

    MINIO_HOST: str
    MINIO_PORT: int
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_PUBLIC_HOST: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def get_minio_endpoint(self) -> str:
        """Возвращает URL для подключения к MinIO"""
        return f"{self.MINIO_HOST}:{self.MINIO_PORT}"

    def get_minio_public_endpoint(self) -> str:
        """Возвращает URL для подключения к MinIO"""
        return f"{self.MINIO_PUBLIC_HOST}:{self.MINIO_PORT}"


@lru_cache
def get_db_settings() -> DatabaseSettings:
    """Возвращает настройки базы данных с ленивой инициализацией"""
    return DatabaseSettings()

@lru_cache
def get_auth_settings() -> AuthSettings:
    """Возвращает настройки аутентификации с ленивой инициализацией"""
    return AuthSettings()

@lru_cache
def get_bot_settings() -> BotSettings:
    """Возвращает настройки бота с ленивой инициализацией"""
    return BotSettings()

@lru_cache
def get_redis_settings() -> RedisSettings:
    """Возвращает настройки Redis с ленивой инициализацией"""
    return RedisSettings()

@lru_cache
def get_minio_settings() -> MinioSettings:
    """Возвращает настройки MinIO с ленивой инициализацией"""
    return MinioSettings()


db_settings = get_db_settings()
auth_settings = get_auth_settings()
bot_settings = get_bot_settings()
redis_settings = get_redis_settings()
minio_settings = get_minio_settings()
