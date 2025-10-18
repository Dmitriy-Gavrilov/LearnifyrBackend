"""Описание таблицы репетитора в БД"""

from sqlalchemy import Integer, String, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base, PersonCommon


class Teacher(PersonCommon, Base):
    """Модель репетитора"""

    avatar_url: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="URL аватара")
    rate: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Ставка за час")
    rating: Mapped[float] = mapped_column(
        Numeric(2, 1), nullable=False, comment="Рейтинг")

    # Уведомления
    review_notification: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="Уведомления об отзывах")
    response_notification: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="Уведомления о принятии откликов")
    archive_lessons_notification: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="Уведомления о завершении уроков")
