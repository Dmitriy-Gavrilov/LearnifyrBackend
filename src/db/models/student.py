"""Описание таблицы студента в БД"""

from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base, PersonCommon


class Student(PersonCommon, Base):
    """Модель студента"""

    # Уведомления
    request_notification: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="Уведомления об откликах")
    review_published_notification: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="Уведомления об опубликованных отзывах")
    archive_lessons_notification: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="Уведомления о завершении уроков")
