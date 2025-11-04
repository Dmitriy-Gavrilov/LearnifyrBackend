"""Описание таблицы студента в БД"""

import random
from sqlalchemy import Boolean, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base, PersonCommon


class Student(PersonCommon, Base):
    """Модель студента"""

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        default=lambda: random.randint(10_000_000, 1_000_000_000),
        comment="ID студента"
    )

    # Уведомления
    request_notification: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="Уведомления об откликах")
    review_published_notification: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="Уведомления об опубликованных отзывах")
    archive_lessons_notification: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="Уведомления о завершении уроков")
