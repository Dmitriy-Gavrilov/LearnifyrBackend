"""Описание базового класса для всех моделей"""

from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    @declared_attr.directive
    @classmethod
    def __tablename__(cls):
        """Определяет имя таблицы"""
        return cls.__name__.lower() + "s"


class PersonCommon:
    """Общие поля студента и репетитора"""

    # Telegram
    telegram_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, unique=True, comment="ID в Telegram")
    telegram_username: Mapped[str | None] = mapped_column(
        String(50), nullable=True, unique=True, comment="Username в Telegram")

    # Общие
    surname: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Фамилия")
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Имя")
    patronymic: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Отчество")
    age: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Возраст")
    bio: Mapped[str | None] = mapped_column(
        String(200), nullable=True, comment="Описание профиля")

    # Авторизация
    refresh_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="ID refresh токена")
    ip: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="IP адрес")

    # Настройки профиля
    active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="Активность")
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="Удален или нет")
