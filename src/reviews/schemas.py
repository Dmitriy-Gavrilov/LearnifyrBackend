"""Схемы для отзывов"""

from pydantic import BaseModel, Field


class CreateReviewRequest(BaseModel):
    """Схема для создания отзыва"""
    teacher_id: int = Field(..., ge=1, le=1_000_000_000, description="ID репетитора")
    rating: int = Field(..., ge=1, le=5, description="Оценка")
    text: str = Field(..., min_length=1, max_length=100, description="Текст отзыва")


class CreateReviewResponse(BaseModel):
    """Схема для ответа на создание отзыва"""
    review_id: int = Field(..., ge=1, le=1_000_000_000, description="ID созданного отзыва")
