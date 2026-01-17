"""Сервисные функции для работы со студентами"""

from fastapi import HTTPException, status
from sqlalchemy import delete, exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.association_tables import hidden_teachers
from src.db.models.review import Review
from src.db.models.student import Student
from src.db.models.matches import Match, MatchStatus
from src.db.models.token import Token

from src.matches.schemas import MatchResponse
from src.matches.service import get_user_matches
from src.schemas import ReviewSchema, UpdateActiveRequest
from src.student.schemas import (
    StudentProfile,
    StudentProfileById,
    UpdateNotificationRequest,
    UpdateStudentRequest
)


async def get_student_related(
    student_id: int,
    session: AsyncSession
) -> tuple[Student, list[Review]]:
    """Получение связанных объектов студента"""
    # Объект студента
    result = await session.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if student is None or student.telegram_username is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    # Отзывы студента
    reviews = list(
        (await session.execute(
            select(Review)
                .where(Review.student_id == student_id, Review.is_published.is_(True))
                .order_by(Review.created_at.desc())
            )
        ).scalars().all()
    )

    return student, reviews

async def get_profile(user_id: int, session: AsyncSession) -> StudentProfile:
    """Получение профиля студента"""
    student, reviews = await get_student_related(user_id, session)
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
        archive_lessons_notification=student.archive_lessons_notification,
        reviews=[ReviewSchema(
            rating=review.rating, text=review.text, created_at=review.created_at)
            for review in reviews]
    )


async def get_profile_by_id(
    user_id: int,
    student_id: int,
    session: AsyncSession
) -> StudentProfileById:
    """ Получение профиля студента от лица репетитора"""
    student, reviews = await get_student_related(student_id, session)
    exists_match = (
        await session.scalar(
            select(
                exists().where(
                    Match.teacher_id == user_id,
                    Match.student_id == student_id,
                )
            )
        )
    )
    if exists_match:
        tg = student.telegram_username
    else:
        tg = None
    return StudentProfileById(
        telegram_username=tg,
        surname=student.surname,
        name=student.name,
        patronymic=student.patronymic,
        age=student.age,
        bio=student.bio,
        reviews=[ReviewSchema(
            rating=review.rating, text=review.text, created_at=review.created_at)
            for review in reviews]
    )


async def get_student_matches(
    user_id: int,
    session: AsyncSession,
    archived: bool = False,
    rejected: bool = False
) -> list[MatchResponse]:
    """Получение списка откликов студента"""
    return await get_user_matches(user_id, "student", session, archived, rejected)


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


async def update_active_profile(user_id: int, data: UpdateActiveRequest, session: AsyncSession) -> None:
    """Активация профиля студента"""
    result = await session.execute(select(Student).where(Student.id == user_id))
    student = result.scalar_one_or_none()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    student.active = data.active
    await session.commit()


async def update_notification(
    user_id: int,
    data: UpdateNotificationRequest,
    session: AsyncSession
) -> None:
    """Обновление уведомлений репетитора"""
    result = await session.execute(select(Student).where(Student.id == user_id))
    student = result.scalar_one_or_none()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    if data.request_notification is not None:
        student.request_notification = data.request_notification
    if data.review_published_notification is not None:
        student.review_published_notification = data.review_published_notification
    if data.archive_lessons_notification is not None:
        student.archive_lessons_notification = data.archive_lessons_notification
    await session.commit()


async def delete_profile(user_id: int, session: AsyncSession) -> None:
    """Удаление профиля студента"""
    result = await session.execute(select(Student).where(Student.id == user_id))
    student = result.scalar_one_or_none()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    # Очистка основной информации
    student.is_deleted = True
    student.telegram_id = None
    student.telegram_username = None

    # Очистка связей
    await session.execute(
        delete(hidden_teachers).where(hidden_teachers.c.student_id == user_id)
    )
    await session.execute(
        delete(Token).where(Token.user_id == user_id)
    )
    await session.execute(
        update(Match).where(Match.student_id == user_id).values(status=MatchStatus.ARCHIVED)
    )

    await session.commit()
