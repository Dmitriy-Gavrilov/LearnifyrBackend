"""Описание таблицы откликов и сотрудничеств в БД"""

from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base


class MatchStatus(str, Enum):
    """Статус отклика"""

    REQUEST = "request"  # Отклик
    ACTIVE = "active"    # Идут занятия
    ARCHIVED = "archived"  # Архив (завершено)
    REJECTED = "rejected"  # Отклонено


class Match(Base):
    """Модель отклика"""

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="NO ACTION"),
        nullable=False,
        comment="ID студента")

    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id", ondelete="NO ACTION"),
        nullable=False,
        comment="ID репетитора")

    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="NO ACTION"),
        nullable=False,
        comment="ID заявки")

    status: Mapped[MatchStatus] = mapped_column(
        SQLEnum(MatchStatus, native_enum=False),
        nullable=False,
        comment="Статус")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, comment="Дата создания")

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, comment="Дата обновления")
