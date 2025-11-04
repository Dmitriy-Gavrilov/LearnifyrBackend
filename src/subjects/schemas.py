"""Схемы для работы с предметами"""

from pydantic import BaseModel, Field


class SubjectSchema(BaseModel):
    """Схема предмета"""
    name: str = Field(..., description="Название предмета")
