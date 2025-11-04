"""Сервисные функции аутентификации"""

import json
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Union

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.settings import redis_settings
from src.dependencies import get_user_by_id, get_user_by_username

from src.integrations.schemas import AuthEvent, BotRegistrationEvent, EventType
from src.integrations.redis import redis_service

from src.auth.schemas import (
    LoginRequest,
    LoginVerifySchema,
    RegisterResponse,
    RegisterSchema,
    VerifySchema
)

from src.db.models.student import Student
from src.db.models.teacher import Teacher
from src.db.models.token import Token, TokenType


async def create_registration_token(
    user_id: int,
    session: AsyncSession
):
    """Создание токена регистрации"""
    raw_token = secrets.token_urlsafe(32)

    # Хэшируем токен для хранения в БД
    hashed_value = hashlib.sha256(raw_token.encode()).hexdigest()

    token = Token(
        value=hashed_value,
        type=TokenType.REGISTRATION,
        user_id=user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=3),
        used=False,
    )

    session.add(token)
    await session.commit()
    await session.refresh(token)

    return raw_token

async def create_confirmation_token(
    user_id: int,
    session: AsyncSession
) -> str:
    """Создание токена подтверждения"""
    # 1. Генерируем 6-значный код подтверждения
    raw_code = f"{secrets.randbelow(1000000):06}"

    # 2. Хэшируем код и сохраняем в Token
    hashed_value = hashlib.sha256(raw_code.encode()).hexdigest()
    token = Token(
        value=hashed_value,
        type=TokenType.CONFIRMATION,
        user_id=user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=3),
        used=False,
    )

    session.add(token)
    await session.commit()
    await session.refresh(token)

    return raw_code


async def verify_token(data: VerifySchema, session: AsyncSession) -> int:
    """Проверка токена"""
    # 1. Хэшируем токен для поиска в БД
    hashed_value = hashlib.sha256(data.token.encode()).hexdigest()

    # 2. Получаем токен из БД
    result = await session.execute(
        select(Token).where(Token.value == hashed_value, Token.type == data.token_type)
    )
    token = result.scalar_one_or_none()

    # 3. Проверяем, что токен найден
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный токен"
        )
    # 4. Проверяем, не использован ли токен
    if token.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Токен уже использован"
        )

    # 5. Проверяем срок действия
    if token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Токен истёк"
        )

    # 6. Помечаем токен как использованный
    token.used = True
    await session.commit()

    return token.user_id


async def register_user(
    data: RegisterSchema,
    session: AsyncSession
) -> RegisterResponse:
    """Регистрация пользователя"""
    user: Union[Student, Teacher]

    # Создание пользователя
    if data.role == "student":
        user = Student(
            surname=data.surname,
            name=data.name,
            patronymic=data.patronymic,
            active=True,
            is_deleted=False,
            request_notification=True,
            review_published_notification=True,
            archive_lessons_notification=True)
    else:
        user = Teacher(
            surname=data.surname,
            name=data.name,
            patronymic=data.patronymic,
            active=True,
            is_deleted=False,
            rating=0,
            review_notification=True,
            response_notification=True,
            archive_lessons_notification=True)

    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Создание токена
    return RegisterResponse(token=await create_registration_token(user.id, session))


async def update_refresh_id(user_id: int, refresh_id: str, session: AsyncSession) -> None:
    """Обновление refresh_id токена пользователя"""
    user = await get_user_by_id(user_id, session)
    user.refresh_id = refresh_id
    await session.commit()


async def update_ip(user_id: int, ip: str, session: AsyncSession) -> None:
    """Обновление IP адреса пользователя"""
    user = await get_user_by_id(user_id, session)
    user.ip = ip
    await session.commit()

async def set_user_telegram(
    user_id: int,
    data: BotRegistrationEvent,
    session: AsyncSession
) -> None:
    """Установка Telegram ID пользователя"""

    user = await get_user_by_id(user_id, session)

    user.telegram_id = data.user_id
    user.telegram_username = data.username

    await session.commit()


async def login_user(data: LoginRequest, session: AsyncSession) -> None:
    """Авторизация пользователя"""
    user = await get_user_by_username(data.username, session)

    await create_confirmation_token(user.id, session)

    if user.telegram_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram ID пользователя не найден"
        )

    auth_event = AuthEvent(
        event_type=EventType.AUTH,
        user_id=user.telegram_id,
        code=await create_confirmation_token(user.id, session),
    )
    await redis_service.xadd(
            redis_settings.STREAM_FROM_BACKEND,
            fields={"payload": json.dumps(auth_event.model_dump())}
        )


async def login_verify_user(data: LoginVerifySchema, session: AsyncSession) -> tuple[int, str]:
    """Проверка кода подтверждения и вход в систему"""
    user_id = await verify_token(
        VerifySchema(
            token=data.token,
            token_type=TokenType.CONFIRMATION
        ),
        session
    )
    user = await get_user_by_id(user_id, session)
    if isinstance(user, Student):
        return user_id, "student"
    return user_id, "teacher"


async def check_user_refresh(user_id: int, ip: str, refresh_id: str, session: AsyncSession) -> None:
    """Проверка refresh_id и IP"""
    user = await get_user_by_id(user_id, session)
    if user.refresh_id != refresh_id or user.ip != ip:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Сессия недействительна"
        )
