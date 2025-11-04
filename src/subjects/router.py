"""Роутер дял взаимодействия с предметами"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_session
from src.subjects.schemas import SubjectSchema
from src.subjects.service import get_subjects

router = APIRouter(prefix="/subjects", tags=["Subjects"])

@router.get("/", summary="Получение списка предметов")
async def get_all_subjects(session: AsyncSession = Depends(get_session)) -> list[SubjectSchema]:
    """
    Получение списка доступных предметов
    """
    return await get_subjects(session)
