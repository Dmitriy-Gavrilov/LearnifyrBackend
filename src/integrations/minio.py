"""Модуль для работы с MinIO"""

from datetime import timedelta
from functools import lru_cache
from io import BytesIO
from uuid import uuid4

from fastapi import UploadFile
from minio import Minio

from src.settings import minio_settings


@lru_cache
def get_minio_client() -> Minio:
    """Создает и кеширует MinIO клиент"""
    return Minio(
        endpoint=minio_settings.get_minio_endpoint(),
        access_key=minio_settings.MINIO_ROOT_USER,
        secret_key=minio_settings.MINIO_ROOT_PASSWORD,
        secure=False,
    )


def generate_object_name(filename: str | None = None) -> str:
    """Создает уникальное имя объекта для хранения"""
    return f"{filename}-{uuid4()}"


async def upload_file(file: UploadFile, bucket_name: str = "avatars") -> str:
    """Загружает файл в MinIO и возвращает имя объекта"""
    client = get_minio_client()
    object_name = generate_object_name(filename=file.filename)
    data = await file.read()
    data_stream = BytesIO(data)

    client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=data_stream,
        length=len(data),
    )

    return object_name


def get_presigned_url(object_name: str, hours: int = 1) -> str:
    """Создает временную ссылку для скачивания"""
    client = Minio(
        endpoint=minio_settings.get_minio_public_endpoint(),  # публичный хост для браузера
        access_key=minio_settings.MINIO_ROOT_USER,
        secret_key=minio_settings.MINIO_ROOT_PASSWORD,
        secure=False,
    )

    url = client.presigned_get_object(
        bucket_name="avatars",
        object_name=object_name,
        expires=timedelta(hours=hours),
    )
    return url


def delete_file(object_name: str) -> None:
    """Удаляет файл из MinIO"""
    client = get_minio_client()
    client.remove_object("avatars", object_name)
