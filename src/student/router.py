"""Роутер для работы со студентами"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import require_role, UserRole, get_session
from src.student.service import (
    activate_profile,
    deactivate_profile,
    get_profile,
    update_profile
)
from src.student.schemas import StudentProfile, UpdateStudentRequest

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/profile", summary="Получение профиля студента")
async def get_student_profile(
    user_id: int = Depends(require_role(UserRole.STUDENT)),
    session: AsyncSession = Depends(get_session)
) -> StudentProfile:
    """
    Получение профиля студента с основной информацией
    """
    return await get_profile(user_id, session)


@router.patch("/profile", summary="Обновление профиля")
async def update_student_profile(
    data: UpdateStudentRequest,
    user_id: int = Depends(require_role(UserRole.STUDENT)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Обновление основной информации в профиле студента:
        - Фамилия
        - Имя
        - Отчество
        - Возраст
        - Описание профиля
    """
    await update_profile(user_id, data, session)


@router.patch("/deactivate", summary="Деактивация профиля")
async def deactivate_student_profile(
    user_id: int = Depends(require_role(UserRole.STUDENT)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Деактивация профиля студента
    """
    await deactivate_profile(user_id, session)


@router.patch("/activate", summary="Активация профиля")
async def activate_student_profile(
    user_id: int = Depends(require_role(UserRole.STUDENT)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Активация профиля студента
    """
    await activate_profile(user_id, session)
