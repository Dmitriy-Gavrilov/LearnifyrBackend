"""Роутер для работы с откликами"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import UserRole, get_session, require_role
from src.matches.service import complete_user_match

router = APIRouter(prefix="/matches", tags=["Applications"])


@router.post("/{match_id}/complete", summary="Завершение отклика")
async def complete_match(
    match_id: int,
    user_id: int = Depends(require_role(UserRole.AUTHORIZED)),
    session: AsyncSession = Depends(get_session)
) -> None:
    """Завершение отклика"""
    return await complete_user_match(match_id, user_id, session)
