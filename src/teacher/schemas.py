"""Схемы для работы с репетиторами"""

from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas import BaseUserResponse, BaseUserUpdate


class ReviewSchema(BaseModel):
    """Схема отзыва"""
    rating: int = Field(..., description="Оценка")
    text: str = Field(..., description="Текст отзыва")
    created_at: datetime = Field(..., description="Дата создания")


class TeacherProfile(BaseUserResponse):
    """Схема профиля репетитора"""

    # Дополнительная информация
    avatar_url: str | None = Field(None, description="Ссылка на изображение")
    rate: int | None = Field(None, description="Ставка за час")
    rating: float = Field(..., description="Рейтинг")

    # Уведомления
    review_notification: bool = Field(..., description="Уведомления об отзывах")
    response_notification: bool = Field(..., description="Уведомления о принятии откликов")
    archive_lessons_notification: bool = Field(..., description="Уведомления о завершении уроков")

    # Предметы
    subjects: list[str] = Field(..., description="Список предметов")

    # Отзывы
    reviews: list[ReviewSchema] = Field(..., description="Список отзывов")


class UpdateTeacherRequest(BaseUserUpdate):
    """Схема обновления профиля репетитора"""

    rate: int | None = Field(None, gt=0, lt=100000, description="Ставка за час")


class UpdateSubjectsRequest(BaseModel):
    """Схема обновления предметов"""
    subjects: list[str] = Field(..., description="Список предметов")


class UpdateNotificationRequest(BaseModel):
    """Схема обновления уведомлений"""
    review_notification: bool | None = Field(
        None,
        description="Уведомления об отзывах"
    )
    response_notification: bool | None = Field(
        None,
        description="Уведомления о принятии откликов"
    )
    archive_lessons_notification: bool | None = Field(
        None,
        description="Уведомления о завершении уроков"
    )
