"""Схемы аутентификации"""

from typing import Literal
from pydantic import BaseModel, Field

from src.db.models.token import TokenType


class RegisterSchema(BaseModel):
    """Схема регистрации"""

    role: Literal["student", "teacher"] = Field(..., description="Роль пользователя")
    surname: str = Field(..., min_length=1, max_length=50, description="Фамилия")
    name: str = Field(..., min_length=1, max_length=50, description="Имя")
    patronymic: str | None = Field(None, max_length=50, description="Отчество")


class RegisterResponse(BaseModel):
    """Схема ответа на регистрацию"""

    token: str = Field(..., description="Токен")


class VerifySchema(BaseModel):
    """Схема проверки токена"""

    token: str = Field(..., description="Токен")
    token_type: TokenType = Field(..., description="Тип токена")


class LoginVerifySchema(BaseModel):
    """Схема проверки кода подтверждения"""

    username: str = Field(..., description="Username в Telegram")
    token: str = Field(..., min_length=6, max_length=6, description="Код подтверждения")


class LoginRequest(BaseModel):
    """Схема авторизации"""

    username: str = Field(..., description="Username в Telegram")


class LoginResponse(BaseModel):
    """Схема ответа на авторизацию"""

    role: str = Field(..., description="Роль пользователя")
