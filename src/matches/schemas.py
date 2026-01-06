"""Схемы для откликов"""

from datetime import datetime

from pydantic import BaseModel, Field


class MatchResponse(BaseModel):
    """Схема отклика"""
    id: int = Field(..., description="ID отклика")
    student_id: int = Field(..., description="ID ученика")
    student_name: str = Field(..., description="Имя ученика")
    student_surname: str = Field(..., description="Фаимилия ученика")
    teacher_id: int = Field(..., description="ID репетитора")
    teacher_name: str = Field(..., description="Имя репетитора")
    teacher_surname: str = Field(..., description="Фаимилия репетитора")
    teacher_patronymic: str | None = Field(None, description="Отчество репетитора")
    subject: str = Field(..., description="Предмет")
    status: str = Field(..., description="Статус отклика")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")
