"""Описание таблицы предметов в БД"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base


class Subject(Base):
    """Модель предмета"""

    name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Название предмета")
