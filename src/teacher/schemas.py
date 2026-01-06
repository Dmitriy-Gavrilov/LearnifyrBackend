"""Схемы для работы с репетиторами"""

from pydantic import BaseModel, Field

from src.schemas import BaseUserResponse, BaseUserSchema, BaseUserUpdate, ReviewSchema


class TeacherInfo(BaseModel):
    """Схема краткого представления преподавателя"""
    id: int = Field(..., description="ID")
    surname: str = Field(..., description="Фамилия")
    name: str = Field(..., description="Имя")
    patronymic: str | None = Field(None, description="Отчество")
    age: int | None = Field(None, description="Возраст")
    avatar_url: str | None = Field(None, description="Ссылка на изображение")
    rating: float = Field(..., description="Рейтинг")


class TeacherProfile(BaseUserResponse):
    """Схема профиля репетитора"""

    # Дополнительная информация
    avatar_url: str | None = Field(None, description="Ссылка на изображение")
    rate: int | None = Field(None, description="Ставка за час")
    rating: float = Field(..., description="Рейтинг")

    # Уведомления
    application_notification: bool = Field(..., description="Уведомления о новых заявках")
    review_notification: bool = Field(..., description="Уведомления об отзывах")
    response_notification: bool = Field(..., description="Уведомления о принятии откликов")
    archive_lessons_notification: bool = Field(..., description="Уведомления о завершении уроков")

    # Предметы
    subjects: list[str] = Field(..., description="Список предметов")

    # Отзывы
    reviews: list[ReviewSchema] = Field(..., description="Список отзывов")


class TeacherByIdProfile(BaseUserSchema):
    """Профиль репетитора от лица ученика"""
    telegram_username: str = Field(..., description="Username в Telegram")

    avatar_url: str | None = Field(None, description="Ссылка на изображение")
    rate: int | None = Field(None, description="Ставка за час")
    rating: float = Field(..., description="Рейтинг")

    subjects: list[str] = Field(..., description="Список предметов")
    reviews: list[ReviewSchema] = Field(..., description="Список отзывов")


class UpdateTeacherRequest(BaseUserUpdate):
    """Схема обновления профиля репетитора"""

    rate: int | None = Field(None, gt=0, lt=100000, description="Ставка за час")


class UpdateSubjectsRequest(BaseModel):
    """Схема обновления предметов"""
    subjects: list[str] = Field(..., description="Список предметов")


class UpdateNotificationRequest(BaseModel):
    """Схема обновления уведомлений"""
    application_notification: bool | None = Field(
        None,
        description="Уведомления о новых заявках"
    )
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
