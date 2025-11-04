"""Роутер аутентификации"""

from fastapi import APIRouter, Response, Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from authx.exceptions import JWTDecodeError
from jose import jwt # type: ignore

from src.dependencies import get_session
from src.auth.service import (
    check_user_refresh,
    login_user,
    login_verify_user,
    register_user,
    update_refresh_id,
    update_ip
)
from src.auth.schemas import (
    LoginRequest,
    LoginResponse,
    LoginVerifySchema,
    RegisterResponse,
    RegisterSchema
)
from src.auth.security import config, security

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", summary="Регистрация пользователя")
async def register(
    data: RegisterSchema,
    session: AsyncSession = Depends(get_session)
) -> RegisterResponse:
    """Регистрация пользователя"""
    return await register_user(data, session)


@router.post("/login", summary="Запрос на получение кода подтверждения")
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_session)
) -> None:
    """Запрос на получение кода подтверждения"""
    await login_user(data, session)


@router.post("/login/verify", summary="Проверка кода подтверждения и вход в систему")
async def login_verify(
    data: LoginVerifySchema,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session)
) -> LoginResponse:
    """Проверка кода подтверждения и вход в систему"""
    user_id, role = await login_verify_user(data, session)

    # Создание токенов
    access_token = security.create_access_token(uid=str(user_id))
    refresh_token = security.create_refresh_token(uid=str(user_id))

    # Обновление refresh_id и IP
    refresh_payload = jwt.get_unverified_claims(refresh_token)
    client_host = request.client.host if request.client else ""  # для mypy, использоваться не будет
    await update_refresh_id(user_id, refresh_payload["jti"], session)
    await update_ip(user_id, client_host, session)

    # Установка токенов в cookies
    security.set_access_cookies(access_token, response)
    security.set_refresh_cookies(refresh_token, response)

    return LoginResponse(role=role)


@router.post("/logout", summary="Выход из системы")
async def logout(
    response: Response
) -> None:
    """Выход из системы"""
    # Удаление токенов из cookies
    security.unset_cookies(response)


@router.post("/refresh", summary="Обновление JWT-токенов")
async def refresh(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session)
) -> None:
    """Обновление токенов"""
    try:
        # Получение токенов из cookies
        refresh_token = await security.get_refresh_token_from_request(request)
        token_payload = security.verify_token(refresh_token, verify_csrf=False)
        user_id = int(token_payload.sub)
        refresh_jti = token_payload.jti or ""  # для mypy, использоваться не будет
        client_host = request.client.host if request.client else ""  # для mypy, использоваться не будет

        # Проверка refresh_id и IP
        await check_user_refresh(user_id, client_host, refresh_jti, session)

        # Создание новых токенов
        new_access_token = security.create_access_token(uid=str(user_id))
        new_refresh_token = security.create_refresh_token(uid=str(user_id))

        # Обновление refresh_id
        refresh_payload = jwt.get_unverified_claims(new_refresh_token)
        await update_refresh_id(user_id, refresh_payload["jti"], session)

        # Установка новых токенов в cookies
        response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
        response.delete_cookie(config.JWT_REFRESH_COOKIE_NAME)
        security.set_access_cookies(new_access_token, response)
        security.set_refresh_cookies(new_refresh_token, response)
    except JWTDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия сессии истек"
        ) from e
