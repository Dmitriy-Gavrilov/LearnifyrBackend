"""Роутер для работы с репетиторами"""

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import require_role, UserRole, get_session
from src.matches.schemas import MatchResponse
from src.schemas import UpdateActiveRequest
from src.teacher.schemas import (
    TeacherByIdProfile,
    TeacherInfo,
    TeacherProfile,
    UpdateNotificationRequest,
    UpdateSubjectsRequest,
    UpdateTeacherRequest
)
from src.teacher.service import (
    delete_profile,
    get_all_teachers,
    get_profile,
    get_profile_by_id,
    get_teacher_matches,
    update_active_profile,
    update_avatar,
    delete_avatar,
    update_notification,
    update_profile,
    update_subjects
)

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.get("")
async def get_teachers(
    _user_id: int = Depends(require_role(UserRole.STUDENT)),
    session: AsyncSession = Depends(get_session)
) -> list[TeacherInfo]:
    """Полученеи списка преподавателей"""
    return await get_all_teachers(session)


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


@router.get("/matches", summary="Получение списка откликов")
async def get_matches(
    archived: bool = Query(False, description="Завершенные"),
    rejected: bool = Query(False, description="Отклоненные"),
    user_id: int = Depends(require_role(UserRole.TEACHER)),
    session: AsyncSession = Depends(get_session)
) -> list[MatchResponse]:
    """Получение списка откликов на заявки"""
    return await get_teacher_matches(user_id, session, archived, rejected)


@router.post("/avatar", summary="Обновление аватара")
async def update_teacher_avatar(
    avatar_file: UploadFile = File(..., description="Изображение"),
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


@router.patch("/active", summary="Изменение активности профиля")
async def update_teacher_active(
    data: UpdateActiveRequest,
    user_id: int = Depends(require_role(UserRole.TEACHER)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Активация и деактивация профиля репетитора
    """
    await update_active_profile(user_id, data, session)


@router.post("/subjects", summary="Обновление предметов")
async def update_teacher_subjects(
    subjects: UpdateSubjectsRequest,
    user_id: int = Depends(require_role(UserRole.TEACHER)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Обновление предметов репетитора
    """
    await update_subjects(user_id, subjects, session)


@router.patch("/notifications", summary="Обновление уведомлений")
async def update_teacher_notification(
    data: UpdateNotificationRequest,
    user_id: int = Depends(require_role(UserRole.TEACHER)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Обновление настроек уведомлений репетитора
    """
    await update_notification(user_id, data, session)


@router.delete("/", summary="Удаление профиля")
async def delete_teacher_profile(
    user_id: int = Depends(require_role(UserRole.TEACHER)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Удаление профиля репетитора
    """
    await delete_profile(user_id, session)


@router.get("/{teacher_id}", summary="Получение профиля репетитора от лица ученика")
async def get_teacher_by_id(
    teacher_id: int,
    _user_id: int = Depends(require_role(UserRole.STUDENT)),
    session: AsyncSession = Depends(get_session)
) -> TeacherByIdProfile:
    """Получение профиля репетитора от лица ученика"""
    return await get_profile_by_id(teacher_id, session)
