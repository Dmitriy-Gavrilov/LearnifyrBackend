"""Зависимости"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db_manager import get_database_manager

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии для работы с базой данных."""
    async with get_database_manager().session_factory() as session:
        yield session
