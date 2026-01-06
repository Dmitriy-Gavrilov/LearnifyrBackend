"""Схемы для обмена сообщениями с Telegram ботом"""

from enum import Enum
from pydantic import BaseModel, Field

class EventType(str, Enum):
    """Типы событий"""
    COMMON_START = "common_start"
    REGISTRATION_START = "registration_start"
    REGISTRATION_FINISH = "registration_finish"
    AUTH = "auth"
    NOTIFICATION = "notification"


class BaseEvent(BaseModel):
    """Базовая схема события"""
    event_type: EventType = Field(..., description="Тип события")


class BotRegistrationEvent(BaseEvent):
    """Сообщение от бота при регистрации"""
    user_id: int = Field(..., description="ID пользователя в Telegram")
    username: str = Field(..., description="Username пользователя в Telegram")
    token: str = Field(..., description="Токен регистрации")

class BotCommonStart(BaseEvent):
    """/start без передачи токена"""
    user_id: int = Field(..., description="ID пользователя в Telegram")
    username: str = Field(..., description="Username пользователя в Telegram")


class RegistrationResponseEvent(BaseEvent):
    """Ответ боту при регистрации"""
    user_id: int = Field(..., description="ID пользователя в Telegram")
    message: str = Field(..., description="Сообщение пользователю")


class AuthEvent(BaseEvent):
    """Сообщение боту при авторизации"""
    user_id: int = Field(..., description="ID пользователя в Telegram")
    code: str = Field(..., description="Код подтверждения")

class NotificationEvent(BaseEvent):
    """Сообщение боту при авторизации"""
    user_id: int = Field(..., description="ID пользователя в Telegram")
    message: str = Field(..., description="Сообщение пользователю")
