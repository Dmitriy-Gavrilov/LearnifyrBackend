"""Сервисные функции для работы с предметами"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.models.subject import Subject
from src.subjects.schemas import SubjectSchema


async def get_subjects(session: AsyncSession) -> list[SubjectSchema]:
    """
    Получение списка предметов
    """
    result = await session.execute(select(Subject))
    subjects = result.scalars().all()
    return [SubjectSchema(name=subject.name) for subject in subjects]
