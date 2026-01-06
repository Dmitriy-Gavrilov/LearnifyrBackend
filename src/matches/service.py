"""Сервисные функции для работы с откликами"""

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.matches import Match, MatchStatus
from src.db.models.student import Student
from src.db.models.teacher import Teacher
from src.matches.schemas import MatchResponse


async def get_user_matches(
    user_id: int,
    role: str,
    session: AsyncSession,
    archived: bool = False,
    rejected: bool = False
) -> list[MatchResponse]:
    """Получение списка откликов"""
    # Базовые статусы
    statuses: list[MatchStatus] = [
        MatchStatus.REQUEST,
        MatchStatus.ACTIVE,
    ]

    if archived:
        statuses.append(MatchStatus.ARCHIVED)

    if rejected:
        statuses.append(MatchStatus.REJECTED)

    query = (
        select(
            Match,
            Student.name.label("student_name"),
            Student.surname.label("student_surname"),
            Teacher.name.label("teacher_name"),
            Teacher.surname.label("teacher_surname"),
            Teacher.patronymic.label("teacher_patronymic"),
        )
        .join(Student, Student.id == Match.student_id)
        .join(Teacher, Teacher.id == Match.teacher_id)
        .where(Match.status.in_(statuses))
        .order_by(Match.created_at.desc())
    )

    if role == "student":
        query = query.where(Match.student_id == user_id)
    elif role == "teacher":
        query = query.where(Match.teacher_id == user_id)

    rows = (await session.execute(query)).all()

    return [
        MatchResponse(
            id=match.id,
            student_id=match.student_id,
            student_name=student_name,
            student_surname=student_surname,
            teacher_id=match.teacher_id,
            teacher_name=teacher_name,
            teacher_surname=teacher_surname,
            teacher_patronymic=teacher_patronymic,
            subject=match.subject,
            status=match.status,
            created_at=match.created_at,
            updated_at=match.updated_at,
        )
        for (
            match,
            student_name,
            student_surname,
            teacher_name,
            teacher_surname,
            teacher_patronymic,
        ) in rows
    ]


async def complete_user_match(
    match_id: int,
    user_id: int,
    session: AsyncSession
) -> None:
    """Завершение отклика"""
    match = await session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отклик не найден")

    if user_id not in (match.student_id, match.teacher_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на завершение отклика"
        )

    match.status = MatchStatus.ARCHIVED
    match.updated_at = datetime.utcnow()
    await session.commit()
