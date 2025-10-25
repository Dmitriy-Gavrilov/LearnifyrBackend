"""Основной мудль приложения"""
import asyncio
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from src.integrations.service import listen_bot_events

from src.auth.router import router as auth_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Контекстный менеджер для управления жизненным циклом приложения."""
    logger.info("Запуск сервера...")

    listen_bot = asyncio.create_task(listen_bot_events())

    yield

    listen_bot.cancel()
    try:
        await listen_bot
    except asyncio.CancelledError:
        logger.info("Остановка прослушивания событий от Telegram-бота...")

    logger.info("Остановка сервера...")


app = FastAPI(lifespan=lifespan,
              debug=True,
              title="Learnifyr")
api_router = APIRouter(prefix="/api")


@app.middleware("http")
async def log_process_time(request: Request, call_next):
    """Логирование времени обработки запроса."""
    start_time = time.time()

    response: Response = await call_next(request)

    process_time = round(time.time() - start_time, 4)
    method = request.method
    path = request.url.path
    code = response.status_code

    logger.info("%s %s %s %ss", method, path, code, process_time)

    return response


@api_router.get("/health")
def health():
    """Проверка работоспособности сервера"""
    return {"status": "ok"}


app.include_router(api_router)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://localhost:3000",
        "https://127.0.0.1:3000",
        "https://localhost",
        "https://127.0.0.1",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost",
        "http://127.0.0.1"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
