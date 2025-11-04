"""Основной мудль приложения"""
import asyncio
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from src.integrations.service import listen_bot_events

from src.auth.router import router as auth_router
from src.teacher.router import router as teacher_router
from src.student.router import router as student_router
from src.subjects.router import router as subjects_router

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Описание тегов для OpenAPI/Swagger
tags_metadata = [
    {
        "name": "Auth",
        "description": "Авторизация, регистрация и refresh",
    },
    {
        "name": "Teachers",
        "description": "Эндпоинты для работы с репетиторами. Доступны пользователям с ролью **TEACHER**",
    },
    {
        "name": "Subjects",
        "description": "Эндпоинты для работы с предметами",
    },
    {
        "name": "Students",
        "description": "Эндпоинты для работы со студентами. Доступны пользователям с ролью **STUDENT**",
    },
    {
        "name": "Monitoring",
        "description": "Эндпоинты для проверки работоспособности приложения",
    },
]

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


app = FastAPI(
    title="Learnifyr",
    debug=True,
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)
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


@api_router.get("/health", tags=["Monitoring"])
def health():
    """Проверка работоспособности сервера"""
    return {"status": "ok"}


api_router.include_router(auth_router)
api_router.include_router(teacher_router)
api_router.include_router(student_router)
api_router.include_router(subjects_router)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://localhost:5173",
        "https://127.0.0.1:5173",
        "https://localhost",
        "https://127.0.0.1",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost",
        "http://127.0.0.1"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
