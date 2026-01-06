"""Схемы для работы со студентами"""

from pydantic import BaseModel, Field

from src.schemas import BaseUserResponse, BaseUserSchema, BaseUserUpdate, ReviewSchema


class StudentProfile(BaseUserResponse):
    """Схема профиля студента"""

    # Уведомления
    request_notification: bool = Field(..., description="Уведомления об откликах")
    review_published_notification: bool = Field(..., description="Уведомления об опубликованных отзывах")
    archive_lessons_notification: bool = Field(..., description="Уведомления о завершении уроков")

    reviews: list[ReviewSchema] = Field(..., description="Список оставленных отзывов")


class StudentProfileById(BaseUserSchema):
    """Схема профиля студента от лица репетитора"""
    reviews: list[ReviewSchema] = Field(..., description="Список оставленных отзывов")


class UpdateStudentRequest(BaseUserUpdate):
    """Схема обновления профиля студента"""


class UpdateNotificationRequest(BaseModel):
    """Схема обновления уведомлений"""
    request_notification: bool | None = Field(
        None,
        description="Уведомления об откликах"
    )
    review_published_notification: bool | None = Field(
        None,
        description="Уведомления об опубликованных отзывах"
    )
    archive_lessons_notification: bool | None = Field(
        None,
        description="Уведомления о завершении уроков"
    )
