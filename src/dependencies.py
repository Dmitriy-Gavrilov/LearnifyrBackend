"""Зависимости"""

from enum import Enum
from typing import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from authx import TokenPayload, RequestToken
from authx.exceptions import MissingTokenError, JWTDecodeError

from src.db.models.student import Student
from src.db.models.teacher import Teacher
from src.db.db_manager import get_database_manager
from src.auth.security import security

class UserRole(str, Enum):
    """Роль пользователя"""
    STUDENT = "student"
    TEACHER = "teacher"
    AUTHORIZED = "authorized"


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии для работы с базой данных."""
    async with get_database_manager().session_factory() as session:
        yield session


@asynccontextmanager
async def get_db_session():
    """Создаёт сессию вне FastAPI-зависимости."""
    gen = get_session()
    session = await gen.__anext__()  # Получаем саму сессию
    try:
        yield session
    finally:
        await gen.aclose()


async def get_user_by_id(user_id: int, session: AsyncSession) -> Student | Teacher:
    """Возвращает пользователя (студент/репетитор) по ID"""
    result = await session.execute(select(Student).where(Student.id == user_id))
    student = result.scalar_one_or_none()
    if student is not None:
        return student

    result = await session.execute(select(Teacher).where(Teacher.id == user_id))
    teacher = result.scalar_one_or_none()
    if teacher is not None:
        return teacher

    # Если ни студент, ни репетитор не найден
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Пользователь не найден"
    )


async def get_user_by_username(username: str, session: AsyncSession) -> Student | Teacher:
    """Возвращает пользователя (студент/репетитор) по username"""
    result = await session.execute(select(Student).where(Student.telegram_username == username))
    student = result.scalar_one_or_none()
    if student is not None:
        return student

    result = await session.execute(select(Teacher).where(Teacher.telegram_username == username))
    teacher = result.scalar_one_or_none()
    if teacher is not None:
        return teacher

    # Если ни студент, ни репетитор не найден
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Пользователь не найден"
    )


async def verify_token(request: Request, session: AsyncSession) -> Student | Teacher:
    """Проверка токена"""
    try:
        # Валидация токена
        token: RequestToken = await security.get_access_token_from_request(request)
        #token.csrf = request.headers.get("X-CSRF-TOKEN")
        token_payload: TokenPayload = security.verify_token(token, verify_csrf=False)
        # Получение пользователя
        user_id = int(token_payload.sub)
        return await get_user_by_id(user_id, session)

    except MissingTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется войти в систему"
        ) from e
    except JWTDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия сеанса истек"
        ) from e


def require_role(required_role: UserRole) -> Callable[[Request, AsyncSession], Awaitable[int]]:
    """Создает зависимость для проверки прав"""
    async def dependency(
            request: Request,
            session: AsyncSession = Depends(get_session)
    ) -> int:
        """Проверка прав пользователя"""
        # if required_role == UserRole.STUDENT:
        #     return 660828911
        current_user = await verify_token(request, session)
        if required_role == UserRole.STUDENT and not isinstance(current_user, Student):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Требуется роль студента"
            )
        if required_role == UserRole.TEACHER and not isinstance(current_user, Teacher):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Требуется роль репетитора"
            )
        if required_role == UserRole.AUTHORIZED:
            pass
        return current_user.id

    return dependency
