"""Модуль взаимодействия с Redis"""

import logging
import asyncio
import json

from fastapi import HTTPException
from sqlalchemy import select

from src.db.models.review import Review
from src.settings import redis_settings
from src.dependencies import get_db_session, get_user_by_username
from src.integrations.redis import read_stream_messages, redis_service
from src.integrations.schemas import (
    BotCommonStart,
    BotReviewResponse,
    EventType,
    BotRegistrationEvent,
    RegistrationResponseEvent,
)
from src.auth.service import set_user_telegram, verify_token
from src.auth.schemas import VerifySchema
from src.db.models.token import TokenType


logger = logging.getLogger(__name__)

async def listen_bot_events():
    """Прослушивание событий от Telegram-бота"""
    last_id = "$"

    logger.info("Запуск прослушивания событий от Telegram-бота")

    while True:
        try:
            messages = await read_stream_messages(
                redis_service,
                redis_settings.STREAM_TO_BACKEND,
                last_id,
            )

            for m_id, fields in messages:
                last_id = m_id
                payload = json.loads(fields[b"payload"].decode())
                event_type = payload["event_type"]
                message = "Неизвестная ошибка"

                logger.info("Получено событие от Telegram-бота: %s", event_type)

                # Обрабатываем события
                if event_type == EventType.REGISTRATION_START:
                    event = BotRegistrationEvent(**payload)
                    message = await handle_registration_start(event)
                elif event_type == EventType.COMMON_START:
                    event = BotCommonStart(**payload)
                    message = await handle_common_start(event)
                elif event_type == EventType.REVIEW_RESPONSE:
                    event = BotReviewResponse(**payload)
                    message = await handle_review_response(event)
                    continue

                # Отправляем ответ обратно в бот
                response = RegistrationResponseEvent(
                    event_type=EventType.REGISTRATION_FINISH,
                    user_id=event.user_id,
                    message=message,
                )
                await redis_service.xadd(
                    redis_settings.STREAM_FROM_BACKEND,
                    fields={"payload": json.dumps(response.model_dump())}
                )

            await asyncio.sleep(0.5)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Ошибка в слушателе Redis: %s", e)


async def handle_registration_start(event: BotRegistrationEvent) -> str:
    """Обработка события регистрации"""
    async with get_db_session() as session:  # создаем новую сессию на каждое событие
        try:
            await get_user_by_username(event.username, session)
            return "Вы уже зарегистрированы. Для входа в систему перейдите на сайт."
        except HTTPException:
            try:
                data = VerifySchema(token=event.token, token_type=TokenType.REGISTRATION)
                user_id = await verify_token(data, session)

                await set_user_telegram(user_id, event, session)

                return "Регистрация успешно завершена"
            except HTTPException as e:
                return f"Ошибка регистрации: {e.detail}"


async def handle_common_start(event: BotCommonStart) -> str:
    """Обработка события регистрации"""
    async with get_db_session() as session:  # создаем новую сессию на каждое событие
        try:
            await get_user_by_username(event.username, session)
            return "Вы уже зарегистрированы. Для входа в систему перейдите на сайт."
        except HTTPException:
            return "Для регистрации в системе перейдите на сайт"

async def handle_review_response(event: BotReviewResponse) -> None:
    """Обработка ответа на отзыв"""
    async with get_db_session() as session:
        review = (await session.execute(
            select(Review).where(Review.id == event.review_id)
        )).scalar_one()
        if event.action == "publish":
            review.is_published = True
        await session.commit()
