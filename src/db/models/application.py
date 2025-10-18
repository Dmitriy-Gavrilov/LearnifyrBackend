"""Описание таблицы заявки в БД"""

from enum import Enum

from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base


class LessonsCount(str, Enum):
    """Количество уроков"""

    FEW = "few"         # 1-3
    MEDIUM = "medium"   # 3-10
    MANY = "many"       # 10+


class ApplicationStatus(str, Enum):
    """Статус заявки"""

    ACTIVE = "active"
    ACCEPTED = "accepted"
    ARCHIVED = "archived"


class Application(Base):
    """Модель заявки"""

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="NO ACTION"),
        nullable=False,
        comment="ID студента")

    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="NO ACTION"),
        nullable=False,
        comment="ID предмета")

    price: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Цена за час")

    lessons_count: Mapped[LessonsCount] = mapped_column(
        SQLEnum(LessonsCount, native_enum=False),
        nullable=False,
        comment="Преподполагаемое количество уроков")

    description: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="Описание")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, comment="Дата создания")

    status: Mapped[ApplicationStatus] = mapped_column(
        SQLEnum(ApplicationStatus, native_enum=False),
        nullable=False,
        comment="Статус заявки")
