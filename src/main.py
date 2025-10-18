"""Основной мудль приложения"""
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, Request, Response
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Контекстный менеджер для управления жизненным циклом приложения."""
    logger.info("Запуск сервера...")

    yield

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
