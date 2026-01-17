"""Сервисные функции для работы с отзывами"""

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.review import Review
from src.db.models.matches import Match, MatchStatus
from src.db.models.teacher import Teacher
from src.integrations.notification import send_review_notification
from src.reviews.schemas import CreateReviewRequest, CreateReviewResponse


async def create_user_review(
    user_id: int,
    data: CreateReviewRequest,
    session: AsyncSession
) -> CreateReviewResponse:
    """Создание отзыва"""
    # Проверка на существование отзыва от студента на этого репетитора
    existing_review = (await session.execute(
        select(Review).where(
            Review.student_id == user_id,
            Review.teacher_id == data.teacher_id
        )
    )).scalar_one_or_none()
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя оставить более 1 отзыва на репетитора"
        )

    # Отзыв можно оставить только после завершенных занятий
    existing_match = (await session.execute(
        select(Match).where(
            Match.student_id == user_id,
            Match.teacher_id == data.teacher_id,
            Match.status == MatchStatus.ARCHIVED
        )
    )).scalars().all()
    if not existing_match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отзыв можно оставить только после завершенных занятий"
        )

    # Создание нового отзыва
    review = Review(
        student_id=user_id,
        teacher_id=data.teacher_id,
        text=data.text,
        rating=data.rating,
        created_at=datetime.utcnow(),
        is_published=False
    )
    session.add(review)
    await session.commit()
    await session.refresh(review)

    teacher = (
        await session.execute(
            select(Teacher).where(Teacher.id == data.teacher_id)
        )
    ).scalar_one()

    if teacher.review_notification:
        # Отправка уведомления репетитору для подтверждения публикации
        await send_review_notification(teacher.telegram_id, f"Новый отзыв:\n{data.text}", review.id)  # type: ignore
    else:
        # Публикация отзыва без подтверждения
        review.is_published = True
        await session.commit()

    return CreateReviewResponse(review_id=review.id)
