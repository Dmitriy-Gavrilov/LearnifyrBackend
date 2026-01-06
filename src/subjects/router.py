"""Роутер дял взаимодействия с предметами"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import UserRole, get_session, require_role
from src.subjects.schemas import SubjectSchema
from src.subjects.service import get_subjects

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("/", summary="Получение списка предметов")
async def get_all_subjects(
    _user_id: int = Depends(require_role(UserRole.AUTHORIZED)),
    session: AsyncSession = Depends(get_session),
) -> list[SubjectSchema]:
    """
    Получение списка доступных предметов
    """
    return await get_subjects(session)
