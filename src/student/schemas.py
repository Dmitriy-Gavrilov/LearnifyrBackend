"""Схемы для работы со студентами"""

from pydantic import Field

from src.schemas import BaseUserResponse, BaseUserUpdate


class StudentProfile(BaseUserResponse):
    """Схема профиля студента"""

    # Уведомления
    request_notification: bool = Field(..., description="Уведомления об откликах")
    review_published_notification: bool = Field(..., description="Уведомления об опубликованных отзывах")
    archive_lessons_notification: bool = Field(..., description="Уведомления о завершении уроков")


class UpdateStudentRequest(BaseUserUpdate):
    """Схема обновления профиля студента"""
