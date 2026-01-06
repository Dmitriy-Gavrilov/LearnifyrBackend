"""Сервис для работы с заявками"""

import asyncio
from datetime import datetime
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, insert, or_, select

from src.applications.schemas import (
    ApplicationFilters,
    ApplicationResponse,
    CreateApplicationRequest,
    CreateApplicationResponse,
    DetailApplicationResponse,
    RequestApplicationResponse,
    UpdateApplicationRequest
)
from src.db.models.application import Application, ApplicationStatus
from src.db.models.matches import Match, MatchStatus
from src.db.models.subject import Subject
from src.db.models.teacher import Teacher
from src.db.models.student import Student
from src.db.models.association_tables import hidden_applications, teacher_subjects
from src.integrations.notification import new_application_newsletter, send_notification


async def find_teachers(
    session: AsyncSession,
    subject_id: int,
    price: int
) -> Sequence[Teacher]:
    """Находит репетиторов для рассылки уведомлений"""
    return (await session.execute(
        select(Teacher)
        .join(teacher_subjects, teacher_subjects.c.teacher_id == Teacher.id)
        .where(
            teacher_subjects.c.subject_id == subject_id,
            Teacher.application_notification.is_(True),
            Teacher.rate.is_not(None),
            Teacher.telegram_id.is_not(None),
            Teacher.rate.between(price * 0.9, price * 1.1)
        )
    )).scalars().all()


async def create_user_application(
    user_id: int,
    data: CreateApplicationRequest,
    session: AsyncSession
) -> CreateApplicationResponse:
    """Создание заявки"""
    subject = (await session.execute(
        select(Subject).where(Subject.name == data.subject_name)
    )).scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден")

    application = Application(
        student_id=user_id,
        subject_id=subject.id,
        price=data.price,
        lessons_count=data.lessons_count,
        description=data.description,
        created_at=datetime.utcnow(),
        status=ApplicationStatus.ACTIVE
    )
    session.add(application)
    await session.commit()
    await session.refresh(application)

    # Рассылка уведомлений репетиторам
    new_application_newsletter(
        teachers=(await find_teachers(session, subject.id, data.price)),
        subject_name=subject.name,
        price=data.price,
        date=application.created_at,
        lessons_count=data.lessons_count
    )

    return CreateApplicationResponse(application_id=application.id)


async def update_user_application(
    application_id: int,
    user_id: int,
    data: UpdateApplicationRequest,
    session: AsyncSession
) -> None:
    """Обновление заявки"""
    application = (await session.execute(
        select(Application).where(Application.id == application_id)
    )).scalar_one_or_none()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )

    if application.student_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Заявка не принадлежит пользователю"
        )

    if data.subject_name:
        subject = (await session.execute(
            select(Subject).where(Subject.name == data.subject_name)
        )).scalar_one_or_none()
        if not subject:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден")
        application.subject_id = subject.id

    if data.price:
        application.price = data.price

    if data.lessons_count:
        application.lessons_count = data.lessons_count

    if data.description:
        application.description = data.description

    application.created_at = datetime.utcnow()
    await session.commit()

    subject_name = data.subject_name or (await session.execute(
        select(Subject.name).where(Subject.id == application.subject_id)
    )).scalar_one()

    # Рассылка уведомлений репетиторам
    new_application_newsletter(
        teachers=(await find_teachers(session, application.subject_id, application.price)),
        subject_name=subject_name,
        price=application.price,
        date=application.created_at,
        lessons_count=application.lessons_count
    )


async def get_user_applications(
    user_id: int,
    session: AsyncSession,
    filters: ApplicationFilters,
    limit: int = 100,
    offset: int = 0
) -> list[ApplicationResponse]:
    """Получение списка заявок"""
    query = (
        select(
            Application,
            Subject.name.label("subject_name")
        )
        .join(Student, Student.id == Application.student_id)
        .join(Subject, Subject.id == Application.subject_id)
        .outerjoin(
            hidden_applications,
            and_(
                hidden_applications.c.application_id == Application.id,
                hidden_applications.c.teacher_id == user_id
            )
        )
        .where(
            Application.status == ApplicationStatus.ACTIVE,
            hidden_applications.c.application_id.is_(None)
        )
        .order_by(
            Application.price.desc(),
            Application.created_at.desc()
        )
    )

    # Фильтры
    if filters.subjects_list:
        query = query.where(Subject.name.in_(filters.subjects_list))

    if filters.price_min is not None:
        query = query.where(Application.price >= filters.price_min)

    if filters.price_max is not None:
        query = query.where(Application.price <= filters.price_max)

    if filters.student_age_min is not None:
        query = query.where(
            or_(
                Student.age >= filters.student_age_min,
                Student.age.is_(None)
            )
        )

    if filters.student_age_max is not None:
        query = query.where(
            or_(
                Student.age <= filters.student_age_max,
                Student.age.is_(None)
            )
        )

    if filters.lessons_counts:
        query = query.where(Application.lessons_count.in_(filters.lessons_counts))

    # Пагинация
    query = query.limit(limit).offset(offset)

    result = await session.execute(query)
    rows = result.all()

    return [
        ApplicationResponse(
            id=app.id,
            subject_name=subject_name,
            price=app.price,
            lessons_count=app.lessons_count,
            created_at=app.created_at,
            status=app.status,
        )
        for app, subject_name in rows
    ]


async def get_user_detail_application(
    application_id: int,
    session: AsyncSession
) -> DetailApplicationResponse:
    """Получение заявки"""
    result = await session.execute(
        select(
            Application,
            Subject.name.label("subject_name"),
            Student.name.label("student_name"),
            Student.surname.label("student_surname")
        )
        .join(Student, Student.id == Application.student_id)
        .join(Subject, Subject.id == Application.subject_id)
        .where(Application.id == application_id)
    )

    row = result.one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )

    application, subject_name, student_name, student_surname = row

    return DetailApplicationResponse(
        id=application.id,
        subject_name=subject_name,
        price=application.price,
        lessons_count=application.lessons_count,
        created_at=application.created_at,
        status=application.status,
        description=application.description,
        student_id=application.student_id,
        student_name=student_name,
        student_surname=student_surname,
    )

async def hide_user_application(
    application_id: int,
    user_id: int,
    session: AsyncSession
) -> None:
    """Скрытие заявки репетитором"""
    stmt = insert(hidden_applications).values(
        application_id=application_id,
        teacher_id=user_id
    )
    await session.execute(stmt)
    await session.commit()

async def request_user_application(
    application_id: int,
    user_id: int,
    session: AsyncSession
) -> RequestApplicationResponse:
    """Отклик на заявку"""
    # Получение заявки
    application = (await session.execute(
        select(Application).where(Application.id == application_id)
    )).scalar_one_or_none()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )

    match = Match(
        student_id=application.student_id,
        teacher_id=user_id,
        application_id=application_id,
        status=MatchStatus.REQUEST,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(match)
    await session.commit()
    await session.refresh(match)

    # Отправка уведомления ученику
    student = (
        await session.execute(
            select(Student).where(
                Student.id == application.student_id,
                Student.telegram_id.is_not(None),
                Student.request_notification.is_(True),
            )
        )
    ).scalar_one_or_none()
    if student is not None:
        asyncio.create_task(send_notification(
            student.telegram_id,  # type: ignore
            f"На вашу заявку №{match.id} откликнулся репетитор"
        ))

    return RequestApplicationResponse(match_id=match.id)


async def accept_user_application(
    application_id: int,
    user_id: int,
    session: AsyncSession
) -> None:
    """Принятие заявки"""
    match = (await session.execute(
        select(Match).where(Match.application_id == application_id)
    )).scalar_one_or_none()
    application = (await session.execute(
        select(Application).where(Application.id == application_id)
    )).scalar_one_or_none()
    if not application or not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )
    if application.student_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Заявка не принадлежит пользователю"
        )
    application.status = ApplicationStatus.ACCEPTED
    match.status = MatchStatus.ACTIVE
    match.updated_at = datetime.utcnow()
    await session.commit()

    # Отправка уведомления репетитору
    teacher = (
        await session.execute(
            select(Teacher).where(
                Teacher.id == match.teacher_id,
                Teacher.telegram_id.is_not(None),
                Teacher.response_notification.is_(True),
            )
        )
    ).scalar_one_or_none()
    if teacher is not None:
        asyncio.create_task(send_notification(
            teacher.telegram_id,  # type: ignore
            f"Ваш отклик на заявку №{match.id} принят"
        ))


async def reject_user_application(
    application_id: int,
    user_id: int,
    session: AsyncSession
) -> None:
    """Отклонение заявки"""
    match = (await session.execute(
        select(Match).where(Match.application_id == application_id)
    )).scalar_one_or_none()
    application = (await session.execute(
        select(Application).where(Application.id == application_id)
    )).scalar_one_or_none()
    if not application or not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )
    if application.student_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Заявка не принадлежит пользователю"
        )
    application.status = ApplicationStatus.ARCHIVED
    match.status = MatchStatus.REJECTED
    match.updated_at = datetime.utcnow()
    await session.commit()
