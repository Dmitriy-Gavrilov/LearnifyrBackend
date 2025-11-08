"""Общие схемы"""

from pydantic import BaseModel, Field

class BaseUserResponse(BaseModel):
    """Базовая схема пользователя"""

    # Telegram
    telegram_username: str = Field(..., description="Username в Telegram")

    # Общие
    surname: str = Field(..., description="Фамилия")
    name: str = Field(..., description="Имя")
    patronymic: str | None = Field(None, description="Отчество")
    age: int | None = Field(None, description="Возраст")
    bio: str | None = Field(None, description="Описание профиля")

    # Настройки профиля
    active: bool = Field(..., description="Активность")


class BaseUserUpdate(BaseModel):
    """Базовая схема обновления пользователя"""

    surname: str | None = Field(None, min_length=1, max_length=50, description="Фамилия")
    name: str | None = Field(None, min_length=1, max_length=50, description="Имя")
    patronymic: str | None = Field(None, min_length=1, max_length=50, description="Отчество")
    age: int | None = Field(None, gt=0, lt=150, description="Возраст")
    bio: str | None = Field(None, min_length=1, max_length=200, description="Описание профиля")


class UpdateActiveRequest(BaseModel):
    """Схема обновления активности"""
    active: bool = Field(..., description="Активность")
