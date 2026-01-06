"""Отправка уведомлений"""

import asyncio
from datetime import datetime
import json
from typing import Sequence

from src.db.models.application import LessonsCount
from src.db.models.teacher import Teacher
from src.integrations.redis import redis_service
from src.integrations.schemas import NotificationEvent, EventType
from src.settings import redis_settings


LESSONS_MAP = {
    LessonsCount.FEW: "1–3",
    LessonsCount.MEDIUM: "3–10",
    LessonsCount.MANY: "10+",
}


async def send_notification(user_id: int, message: str) -> None:
    """Отправка уведомления"""
    await redis_service.xadd(
        redis_settings.STREAM_FROM_BACKEND,
        fields={"payload": json.dumps(NotificationEvent(
            event_type=EventType.NOTIFICATION,
            user_id=user_id,
            message=message
        ).model_dump())}
    )


async def notify_teachers(ids: list[int], message: str) -> None:
    """Отправка уведомления репетиторам"""
    for i in ids:
        await send_notification(i, message)


def new_application_newsletter(
    teachers: Sequence[Teacher],
    subject_name: str,
    price: int,
    date: datetime,
    lessons_count: LessonsCount
) -> None:
    """Рассылка уведомлений о новой заявке"""
    dt_str = date.astimezone().strftime("%d.%m.%Y %H:%M")
    lessons_str = LESSONS_MAP[lessons_count]

    text = (
        "<b>Найдена новая заявка</b>\n"
        f"<b>Предмет:</b> {subject_name}\n"
        f"<b>Цена:</b> {price} ₽/час\n"
        f"<b>Количество уроков:</b> {lessons_str}\n"
        f"<b>Опубликована:</b> {dt_str}"
    )
    asyncio.create_task(notify_teachers(
        [t.telegram_id for t in teachers if t.telegram_id is not None], text
    ))
