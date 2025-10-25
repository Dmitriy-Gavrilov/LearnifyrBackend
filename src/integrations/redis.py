"""Redis сервис"""

from redis.asyncio import Redis
from src.settings import redis_settings


class RedisService:
    """Класс для работы с Redis"""

    def __init__(self):
        """Инициализация Redis"""
        self.redis_client = Redis(
            host=redis_settings.REDIS_HOST,
            port=redis_settings.REDIS_PORT,
            password=redis_settings.REDIS_PASSWORD,
            decode_responses=False,  # оставляем False для stream/xadd
            max_connections=100,
        )

    async def xadd(self, stream: str, fields: dict):
        """Добавление сообщения в stream"""
        await self.redis_client.xadd(stream, fields=fields, maxlen=500)

    async def xread(self, stream: str, last_id: str, count: int = 10, block: int = 5000):
        """Чтение сообщений из stream"""
        return await self.redis_client.xread({stream: last_id}, count=count, block=block)


async def read_stream_messages(
    redis_s: RedisService,
    stream: str,
    last_id: str
) -> list[tuple[str, dict[bytes, bytes]]]:
    """Чтение сообщений из stream"""
    result = await redis_s.xread(stream, last_id)
    if not result:
        return []

    messages_list: list[tuple[str, dict[bytes, bytes]]] = []

    for _stream_name, messages in result:
        for msg_id, fields in messages:
            messages_list.append((msg_id, fields))

    return messages_list

redis_service: RedisService = RedisService()
