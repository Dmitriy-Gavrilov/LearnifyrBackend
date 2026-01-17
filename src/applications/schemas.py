"""Схемы для работы с заявками"""

from datetime import datetime

from pydantic import BaseModel, Field

from src.db.models.application import ApplicationStatus, LessonsCount


class CreateApplicationResponse(BaseModel):
    """Схема ответа на создание заявки"""
    application_id: int = Field(..., description="ID заявки")


class ApplicationFilters(BaseModel):
    """Фильтры для получения заявки"""
    subjects: str | None = Field(None, description="Список предметов через запятую")
    price_min: int | None = Field(None, ge=0, le=100000, description="Нижняя граница цены")
    price_max: int | None = Field(None, ge=0, le=100000, description="Верхняя граница цены")
    student_age_min: int | None = Field(None, ge=0, le=150, description="Нижняя граница возраста")
    student_age_max: int | None = Field(None, ge=0, le=150, description="Верхняя граница возраста")
    lessons_counts: str | None = Field(None, description="Количество уроков через запятую")

    @property
    def subjects_list(self) -> list[str] | None:
        """Возвращает список предметов"""
        if self.subjects is None:
            return None
        return [s.strip() for s in self.subjects.split(",") if s.strip()]  # pylint: disable=no-member

    @property
    def lessons_counts_list(self) -> list[LessonsCount] | None:
        """Возвращает список количеств уроков"""
        if self.lessons_counts is None:
            return None
        return [LessonsCount(s.strip()) for s in self.lessons_counts.split(",") if s.strip()]  # pylint: disable=no-member


class StudentApplicationFilters(BaseModel):
    """Фильтры для получения заявок ученика"""
    archived: bool | None = Field(None, description="Закрытые")


class ApplicationResponse(BaseModel):
    """Схема заявки"""
    id: int = Field(..., description="ID заявки")
    subject_name: str = Field(..., description="Название предмета")
    price: int = Field(..., description="Цена за час")
    lessons_count: LessonsCount = Field(..., description="Количество уроков")
    created_at: datetime = Field(..., description="Дата создания")
    status: ApplicationStatus = Field(..., description="Статус заявки")


class DetailApplicationResponse(ApplicationResponse):
    """Cхема детального описания заявки"""
    description: str = Field(..., description="Описание")
    student_id: int = Field(..., description="ID ученика")
    student_name: str = Field(..., description="Имя ученика")
    student_surname: str = Field(..., description="Фаимилия ученика")


class CreateApplicationRequest(BaseModel):
    """Схема создания заявки"""
    subject_name: str = Field(..., description="Название предмета")
    price: int = Field(..., gt=0, lt=100000, description="Цена за час")
    lessons_count: LessonsCount = Field(..., description="Количество уроков")
    description: str = Field(..., max_length=200, description="Описание")


class UpdateApplicationRequest(BaseModel):
    """Схема обновления заявки"""
    subject_name: str | None = Field(None, description="Название предмета")
    price: int | None = Field(None, gt=0, lt=100000, description="Цена за час")
    lessons_count: LessonsCount | None = Field(None, description="Количество уроков")
    description: str | None = Field(None, max_length=200, description="Описание")

class RequestApplicationResponse(BaseModel):
    """Схема ответа на отклик на заявку"""
    match_id: int = Field(..., description="ID (№) отклика")
