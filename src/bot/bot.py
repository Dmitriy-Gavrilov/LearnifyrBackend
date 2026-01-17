"""Telegram Бот"""

import logging
import asyncio
import json
from typing import Union

from aiogram import F, Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.integrations.schemas import (
    BotCommonStart,
    BotReviewResponse,
    EventType,
    BotRegistrationEvent,
    AuthEvent,
    NotificationEvent,
    RegistrationResponseEvent,
    ReviewEvent,
)
from src.integrations.redis import RedisService, read_stream_messages
from src.settings import redis_settings, bot_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_service = RedisService()

# Инициализация бота
bot = Bot(token=bot_settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def send_to_backend(payload: dict):
    """Отправка события бэкенду"""
    await redis_service.xadd(redis_settings.STREAM_TO_BACKEND,
     fields={"payload": json.dumps(payload)})


async def listen_backend_events():
    """Прослушивание событий от бэкенда"""
    last_id = "$"

    logger.info("БОТ: Запуск прослушивания событий от бэкенда")

    while True:
        try:
            messages = await read_stream_messages(
                redis_service,
                redis_settings.STREAM_FROM_BACKEND,
                last_id,
            )

            for msg_id, fields in messages:
                last_id = msg_id
                payload = json.loads(fields[b"payload"].decode())
                event_type = payload["event_type"]

                if event_type == EventType.REGISTRATION_FINISH:
                    event = RegistrationResponseEvent(**payload)
                    await bot.send_message(chat_id=event.user_id, text=event.message)
                elif event_type == EventType.AUTH:
                    event = AuthEvent(**payload)
                    await handle_auth_event(event)
                elif event_type == EventType.NOTIFICATION:
                    event = NotificationEvent(**payload)
                    await handle_notification_event(event)
                elif event_type == EventType.REVIEW:
                    event = ReviewEvent(**payload)
                    await handle_review_event(event)

            await asyncio.sleep(2)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("БОТ: Ошибка прослушивания Redis: %s", e)


async def handle_auth_event(event: AuthEvent):
    """Отправка пользователю 6-значного кода"""
    text = f"Ваш код подтверждения:\n<pre>{event.code}</pre>"
    await bot.send_message(chat_id=event.user_id, text=text)


async def handle_notification_event(event: NotificationEvent):
    """Отправка уведомления пользователю"""
    await bot.send_message(chat_id=event.user_id, text=event.message)


async def handle_review_event(event: ReviewEvent):
    """Отправка уведомления пользователю о новом отзыве"""
    await bot.send_message(
        chat_id=event.user_id,
        text=event.message,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Опубликовать",
                        callback_data=f"review_publish:{event.review_id}",
                    ),
                    InlineKeyboardButton(
                        text="❌ Отклонить",
                        callback_data=f"review_reject:{event.review_id}",
                    ),
                ]
            ]
        )
    )


@dp.callback_query(F.data.startswith("review_"))
async def review_action_handler(callback: CallbackQuery):
    """Обработка ответа на публикацию отзыва"""
    action, review_id = callback.data.split(":")  # type: ignore[union-attr]
    review_id = int(review_id)

    if action == "review_publish":
        event = BotReviewResponse(
            event_type=EventType.REVIEW_RESPONSE,
            review_id=review_id,
            user_id=callback.from_user.id,
            action="publish"
        )
        text = "✅ Отзыв опубликован"
    else:  # action == "review_reject"
        event = BotReviewResponse(
            event_type=EventType.REVIEW_RESPONSE,
            review_id=review_id,
            user_id=callback.from_user.id,
            action="reject"
        )
        text = "❌ Отзыв отклонён"

    await send_to_backend(event.model_dump())

    await callback.answer()
    await bot.send_message(
        chat_id=callback.from_user.id,
        text=text
    )


@dp.message(Command("start"))
async def cmd_start(message: Message, command: CommandObject):
    """Пользователь зашел по ссылке с токеном"""
    token = command.args

    logger.info("БОТ: Пользователь зашел по ссылке с токеном: %s", token)
    if message.from_user is None:  # для mypy, использоваться не будет
        return

    event: Union[BotRegistrationEvent, BotCommonStart]
    if token:
        event = BotRegistrationEvent(
            event_type=EventType.REGISTRATION_START,
            user_id=message.from_user.id,
            username=str(message.from_user.username),
            token=token,
        )
    else:
        event = BotCommonStart(
            event_type=EventType.COMMON_START,
            user_id=message.from_user.id,
            username=str(message.from_user.username),
        )

    await send_to_backend(event.model_dump())


async def main():
    """Основная функция для запуска бота"""

    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(listen_backend_events())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
