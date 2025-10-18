"""Модуль взаимодействия с базой данных."""

from functools import lru_cache

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.settings import db_settings

class DatabaseManager:
    """Вспомогательный класс для работы с базой данных."""

    def __init__(self, url: str, echo: bool = False):
        """Инициализирует подключение к базе данных.

        Args:
            url: URL для подключения к базе данных
            echo: Флаг для вывода SQL-запросов в консоль
        """
        self.engine = create_async_engine(url=url, echo=echo, pool_pre_ping=True)
        self.session_factory = async_sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )


@lru_cache()
def get_database_manager() -> DatabaseManager:
    """Получение менеджера базы данных."""
    return DatabaseManager(url=db_settings.get_db_url())
