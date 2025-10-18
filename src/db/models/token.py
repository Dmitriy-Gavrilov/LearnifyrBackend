"""Описание таблицы токенов в БД
   Хранятся:
    - токены для перехода в бота (регистрация)
    - коды подтверждения регистрации и авторизации
"""

from enum import Enum
from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base


class TokenType(str, Enum):
    """Тип токена"""
    REGISTRATION = "registration"
    CONFIRMATION = "confirmation"


class Token(Base):
    """Модель токена"""

    value: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="Токен")
    type: Mapped[TokenType] = mapped_column(
        SQLEnum(TokenType, native_enum=False),
        nullable=False,
        comment="Тип токена")
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Время истечения")
