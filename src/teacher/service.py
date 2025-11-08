"""Сервисные функции для работы с репетиторами"""

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import delete, insert, join, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.matches import Match, MatchStatus
from src.db.models.token import Token
from src.db.models.review import Review
from src.db.models.teacher import Teacher
from src.db.models.subject import Subject
from src.db.models.association_tables import hidden_applications, hidden_teachers, teacher_subjects

from src.integrations.minio import delete_file, get_presigned_url, upload_file
from src.schemas import UpdateActiveRequest
from src.teacher.schemas import (
    ReviewSchema,
    TeacherProfile,
    UpdateNotificationRequest,
    UpdateSubjectsRequest,
    UpdateTeacherRequest
)


async def get_profile(user_id: int, session: AsyncSession) -> TeacherProfile:
    """Получение профиля репетитора"""

    # Объект репетитора
    result = await session.execute(select(Teacher).where(Teacher.id == user_id))
    teacher = result.scalar_one_or_none()
    if teacher is None or teacher.telegram_username is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    # Аватар
    if teacher.avatar_url is not None:
        avatar_url = get_presigned_url(
            object_name=teacher.avatar_url
        )
    else:
        avatar_url = None

    # Отзывы репетитора
    reviews = list(
        (await session.execute(select(Review).where(Review.teacher_id == user_id)))
        .scalars()
        .all()
    )

    # Предметы, которые ведет репетитор
    subject_result = await session.execute(
        select(Subject.name)
        .select_from(
            join(teacher_subjects, Subject, teacher_subjects.c.subject_id == Subject.id)
        )
        .where(teacher_subjects.c.teacher_id == user_id)
    )
    subjects = [row[0] for row in subject_result.all()]

    return TeacherProfile(
        telegram_username=teacher.telegram_username,
        surname=teacher.surname,
        name=teacher.name,
        patronymic=teacher.patronymic,
        age=teacher.age,
        bio=teacher.bio,
        active=teacher.active,
        avatar_url=avatar_url,
        rate=teacher.rate,
        rating=teacher.rating,
        review_notification=teacher.review_notification,
        response_notification=teacher.response_notification,
        archive_lessons_notification=teacher.archive_lessons_notification,
        subjects=subjects,
        reviews=[ReviewSchema(
            rating=review.rating, text=review.text, created_at=review.created_at)
            for review in reviews]
    )


async def update_avatar(user_id: int, avatar_file: UploadFile, session: AsyncSession) -> None:
    """Обновление аватара репетитора"""
    result = await session.execute(select(Teacher).where(Teacher.id == user_id))
    teacher = result.scalar_one_or_none()
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    if teacher.avatar_url is not None:
        delete_file(teacher.avatar_url)
    teacher.avatar_url = await upload_file(avatar_file)
    await session.commit()


async def delete_avatar(user_id: int, session: AsyncSession) -> None:
    """Удаление аватара репетитора"""
    result = await session.execute(select(Teacher).where(Teacher.id == user_id))
    teacher = result.scalar_one_or_none()
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    if teacher.avatar_url is not None:
        delete_file(teacher.avatar_url)
    teacher.avatar_url = None
    await session.commit()


async def update_profile(user_id: int, profile: UpdateTeacherRequest, session: AsyncSession) -> None:
    """Обновление профиля репетитора"""
    result = await session.execute(select(Teacher).where(Teacher.id == user_id))
    teacher = result.scalar_one_or_none()
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    if profile.surname is not None:
        teacher.surname = profile.surname
    if profile.name is not None:
        teacher.name = profile.name
    if profile.patronymic is not None:
        teacher.patronymic = profile.patronymic
    if profile.age is not None:
        teacher.age = profile.age
    if profile.bio is not None:
        teacher.bio = profile.bio
    if profile.rate is not None:
        teacher.rate = profile.rate
    await session.commit()


async def update_active_profile(user_id: int, data: UpdateActiveRequest, session: AsyncSession) -> None:
    """Активация профиля репетитора"""
    result = await session.execute(select(Teacher).where(Teacher.id == user_id))
    teacher = result.scalar_one_or_none()
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    teacher.active = data.active
    await session.commit()


async def update_subjects(user_id: int, data: UpdateSubjectsRequest, session: AsyncSession) -> None:
    """Обновление предметов репетитора"""
    # Удаляем все прошлые связи
    await session.execute(
        delete(teacher_subjects).where(teacher_subjects.c.teacher_id == user_id)
    )

    # Если список пуст
    if not data.subjects:
        await session.commit()
        return

    # Ищем предметы
    result = await session.execute(
        select(Subject.id, Subject.name).where(Subject.name.in_(data.subjects))
    )
    found_subjects = result.all()

    # Добавляем новые связи
    await session.execute(
        insert(teacher_subjects),
        [{"teacher_id": user_id, "subject_id": sid} for sid, _ in found_subjects],
    )

    await session.commit()


async def update_notification(
    user_id: int,
    data: UpdateNotificationRequest,
    session: AsyncSession
) -> None:
    """Обновление уведомлений репетитора"""
    result = await session.execute(select(Teacher).where(Teacher.id == user_id))
    teacher = result.scalar_one_or_none()
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    if data.review_notification is not None:
        teacher.review_notification = data.review_notification
    if data.response_notification is not None:
        teacher.response_notification = data.response_notification
    if data.archive_lessons_notification is not None:
        teacher.archive_lessons_notification = data.archive_lessons_notification
    await session.commit()


async def delete_profile(user_id: int, session: AsyncSession) -> None:
    """Удаление профиля репетитора"""
    result = await session.execute(select(Teacher).where(Teacher.id == user_id))
    teacher = result.scalar_one_or_none()
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    # Очистка основной информации
    teacher.is_deleted = True
    teacher.telegram_id = None
    teacher.telegram_username = None

    # Удаление аватара
    await delete_avatar(user_id, session)

    # Очистка связей
    await session.execute(
        delete(teacher_subjects).where(teacher_subjects.c.teacher_id == user_id)
    )
    await session.execute(
        delete(hidden_applications).where(hidden_applications.c.teacher_id == user_id)
    )
    await session.execute(
        delete(hidden_teachers).where(hidden_teachers.c.teacher_id == user_id)
    )
    await session.execute(
        delete(Token).where(Token.user_id == user_id)
    )
    await session.execute(
        update(Match).where(Match.teacher_id == user_id).values(status=MatchStatus.ARCHIVED)
    )

    await session.commit()
