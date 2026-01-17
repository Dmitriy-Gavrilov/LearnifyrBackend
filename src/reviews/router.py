"""Роутер для работы с отзывами"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import UserRole, get_session, require_role
from src.reviews.schemas import CreateReviewRequest, CreateReviewResponse
from src.reviews.service import create_user_review

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", summary="Оставить отзыв")
async def create_review(
    data: CreateReviewRequest,
    user_id: int = Depends(require_role(UserRole.STUDENT)),
    session: AsyncSession = Depends(get_session)
) -> CreateReviewResponse:
    """Оставить отзыв"""
    return await create_user_review(user_id, data, session)
