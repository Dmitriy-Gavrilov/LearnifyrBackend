"""Роутер для работы со студентами"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import UpdateActiveRequest
from src.dependencies import require_role, UserRole, get_session
from src.student.service import (
    delete_profile,
    update_active_profile,
    get_profile,
    update_notification,
    update_profile
)
from src.student.schemas import StudentProfile, UpdateNotificationRequest, UpdateStudentRequest

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


@router.patch("/active", summary="Изменение активности профиля")
async def update_student_active(
    data: UpdateActiveRequest,
    user_id: int = Depends(require_role(UserRole.STUDENT)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Активация и деактивация профиля студента
    """
    await update_active_profile(user_id, data, session)


@router.patch("/notification", summary="Обновление уведомлений")
async def update_student_notification(
    data: UpdateNotificationRequest,
    user_id: int = Depends(require_role(UserRole.STUDENT)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Обновление настроек уведомлений студента
    """
    await update_notification(user_id, data, session)

@router.delete("/", summary="Удаление профиля")
async def delete_student_profile(
    user_id: int = Depends(require_role(UserRole.STUDENT)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Удаление профиля студента
    """
    await delete_profile(user_id, session)
