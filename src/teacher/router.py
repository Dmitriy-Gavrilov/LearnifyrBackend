"""Роутер для работы с репетиторами"""

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.teacher.schemas import TeacherProfile, UpdateSubjectsRequest, UpdateTeacherRequest
from src.dependencies import require_role, UserRole, get_session
from src.teacher.service import (
    activate_profile,
    deactivate_profile,
    get_profile,
    update_avatar,
    delete_avatar,
    update_profile,
    update_subjects
)

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.get("/profile", summary="Получение профиля репетитора")
async def get_teacher_profile(
    user_id: int = Depends(require_role(UserRole.TEACHER)),
    session: AsyncSession = Depends(get_session)
) -> TeacherProfile:
    """
    Получение профиля репетитора:
        - Основная информация
        - Ссылка на аватар
        - Отзывы
        - Предметы
    """
    return await get_profile(user_id, session)


@router.post("/update-avatar", summary="Обновление аватара")
async def update_teacher_avatar(
    avatar_file: UploadFile,
    user_id: int = Depends(require_role(UserRole.TEACHER)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Обновление аватара репетитора:
        - Если аватар не существует - создастся
        - Если аватар уже существует - обновится
    """
    await update_avatar(user_id, avatar_file, session)


@router.delete("/avatar", summary="Удаление аватара")
async def delete_teacher_avatar(
    user_id: int = Depends(require_role(UserRole.TEACHER)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Удаление аватара репетитора
    """
    await delete_avatar(user_id, session)


@router.patch("/profile", summary="Обновление профиля")
async def update_teacher_profile(
    data: UpdateTeacherRequest,
    user_id: int = Depends(require_role(UserRole.TEACHER)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Обновление основной информации в профиле репетитора:
        - Фамилия
        - Имя
        - Отчество
        - Возраст
        - Описание профиля
        - Ставка за час
    """
    await update_profile(user_id, data, session)


@router.patch("/deactivate", summary="Деактивация профиля")
async def deactivate_teacher_profile(
    user_id: int = Depends(require_role(UserRole.TEACHER)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Деактивация профиля репетитора
    """
    await deactivate_profile(user_id, session)


@router.patch("/activate", summary="Активация профиля")
async def activate_teacher_profile(
    user_id: int = Depends(require_role(UserRole.TEACHER)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Активация профиля репетитора
    """
    await activate_profile(user_id, session)


@router.post("/update-subjects", summary="Обновление предметов")
async def update_teacher_subjects(
    subjects: UpdateSubjectsRequest,
    user_id: int = Depends(require_role(UserRole.TEACHER)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Обновление предметов репетитора
    """
    await update_subjects(user_id, subjects, session)
