"""Описание таблицы отзывов в БД"""

from datetime import datetime

from sqlalchemy import Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base


class Review(Base):
    """Модель отзыва"""

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="DO NOTHING"),
        nullable=False,
        comment="ID студента, оставившего отзыв")
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID репетитора, которому оставлен отзыв")
    rating: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Оценка")
    text: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Текст отзыва")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, comment="Дата создания")
    is_published: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="Опубликован или нет")
