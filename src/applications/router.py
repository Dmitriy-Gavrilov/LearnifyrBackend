"""Роутер для работы с заявками"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import require_role, UserRole, get_session
from src.applications.service import (
    accept_user_application,
    create_user_application,
    get_user_applications,
    get_user_detail_application,
    hide_user_application,
    reject_user_application,
    request_user_application,
    update_user_application
)
from src.applications.schemas import (
    ApplicationFilters,
    ApplicationResponse,
    CreateApplicationRequest,
    CreateApplicationResponse,
    DetailApplicationResponse,
    RequestApplicationResponse,
    UpdateApplicationRequest
)

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("", summary="Получение списка заявок")
async def get_applications(
    filters: ApplicationFilters = Query(),
    user_id: int = Depends(require_role(UserRole.TEACHER)),
    session: AsyncSession = Depends(get_session)
) -> list[ApplicationResponse]:
    """Получение списка заявок"""
    return await get_user_applications(user_id, session, filters)


@router.get("/{application_id}", summary="Получение заявки")
async def get_application(
    application_id: int,
    _user_id: int = Depends(require_role(UserRole.AUTHORIZED)),
    session: AsyncSession = Depends(get_session)
) -> DetailApplicationResponse:
    """Получение заявки"""
    return await get_user_detail_application(application_id, session)


@router.post("", summary="Создание заявки")
async def create_application(
    data: CreateApplicationRequest,
    user_id: int = Depends(require_role(UserRole.STUDENT)),
    session: AsyncSession = Depends(get_session)
) -> CreateApplicationResponse:
    """Создание новой заявки"""
    return await create_user_application(user_id, data, session)


@router.patch("/{application_id}", summary="Обновление заявки")
async def update_application(
    application_id: int,
    data: UpdateApplicationRequest,
    user_id: int = Depends(require_role(UserRole.STUDENT)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """Обновление заявки"""
    await update_user_application(application_id, user_id, data, session)


@router.post("/{application_id}/request", summary="Откликнуться на заявку")
async def request_application(
    application_id: int,
    user_id: int = Depends(require_role(UserRole.TEACHER)),
    session: AsyncSession = Depends(get_session)
) -> RequestApplicationResponse:
    """Откликнуться на заявку"""
    return await request_user_application(application_id, user_id, session)


@router.post("/{application_id}/hide", summary="Скрыть заявку")
async def hide_application(
    application_id: int,
    user_id: int = Depends(require_role(UserRole.TEACHER)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """Скрыть заявку"""
    await hide_user_application(application_id, user_id, session)


@router.post("/{application_id}/accept", summary="Принять заявку")
async def accept_application(
    application_id: int,
    user_id: int = Depends(require_role(UserRole.STUDENT)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """Принять заявку"""
    await accept_user_application(application_id, user_id, session)


@router.post("/{application_id}/reject", summary="Отклонить заявку")
async def reject_application(
    application_id: int,
    user_id: int = Depends(require_role(UserRole.STUDENT)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """Отклонить заявку"""
    await reject_user_application(application_id, user_id, session)
