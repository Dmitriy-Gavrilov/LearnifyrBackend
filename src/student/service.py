"""Сервисные функции для работы со студентами"""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.student import Student
from src.student.schemas import StudentProfile, UpdateStudentRequest

async def get_profile(user_id: int, session: AsyncSession) -> StudentProfile:
    """Получение профиля студента"""

    # Объект студента
    result = await session.execute(select(Student).where(Student.id == user_id))
    student = result.scalar_one_or_none()
    if student is None or student.telegram_username is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    return StudentProfile(
        telegram_username=student.telegram_username,
        surname=student.surname,
        name=student.name,
        patronymic=student.patronymic,
        age=student.age,
        bio=student.bio,
        active=student.active,
        request_notification=student.request_notification,
        review_published_notification=student.review_published_notification,
        archive_lessons_notification=student.archive_lessons_notification
    )


async def update_profile(user_id: int, profile: UpdateStudentRequest, session: AsyncSession) -> None:
    """Обновление профиля студента"""
    result = await session.execute(select(Student).where(Student.id == user_id))
    student = result.scalar_one_or_none()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    if profile.surname is not None:
        student.surname = profile.surname
    if profile.name is not None:
        student.name = profile.name
    if profile.patronymic is not None:
        student.patronymic = profile.patronymic
    if profile.age is not None:
        student.age = profile.age
    if profile.bio is not None:
        student.bio = profile.bio
    await session.commit()


async def deactivate_profile(user_id: int, session: AsyncSession) -> None:
    """Деактивация профиля студента"""
    result = await session.execute(select(Student).where(Student.id == user_id))
    student = result.scalar_one_or_none()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    student.active = False
    await session.commit()


async def activate_profile(user_id: int, session: AsyncSession) -> None:
    """Активация профиля студента"""
    result = await session.execute(select(Student).where(Student.id == user_id))
    student = result.scalar_one_or_none()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    student.active = True
    await session.commit()
