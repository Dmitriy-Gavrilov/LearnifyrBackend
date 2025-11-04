"""Конфигурация AuthX"""

from authx import AuthX, AuthXConfig

from src.settings import auth_settings

config = AuthXConfig(
    JWT_ALGORITHM='HS256',
    JWT_SECRET_KEY=auth_settings.JWT_SECRET_KEY,
    JWT_COOKIE_SAMESITE="strict",
    JWT_COOKIE_SECURE=False,
    JWT_ACCESS_COOKIE_NAME=auth_settings.JWT_COOKIE_ACCESS_NAME,
    JWT_REFRESH_COOKIE_NAME=auth_settings.JWT_COOKIE_REFRESH_NAME,
    JWT_TOKEN_LOCATION=['cookies'],
    JWT_COOKIE_CSRF_PROTECT=False,
    JWT_ACCESS_TOKEN_EXPIRES=auth_settings.JWT_ACCESS_TOKEN_EXPIRES,
    JWT_REFRESH_TOKEN_EXPIRES=auth_settings.JWT_REFRESH_TOKEN_EXPIRES,
    JWT_COOKIE_MAX_AGE=auth_settings.JWT_COOKIE_MAX_AGE,
)

security: AuthX = AuthX(config=config)
