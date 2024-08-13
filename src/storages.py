import logging
from pathlib import Path
from typing import AsyncGenerator

import aiofiles
from aiofiles.os import path, remove
from fastapi import HTTPException, UploadFile

logger = logging.getLogger(__name__)


class CloudStorage:

    @staticmethod
    async def upload_file(file_location: Path) -> None:
        """Метод для загрузки файла в облако по API"""
        # Код заливки файла в облако (дёргаем API и грузим с диска файл)
        logger.info(f"Файл {file_location.name} загружен в облако")


class LocalStorage:

    @staticmethod
    async def save_file(file: UploadFile, file_location: Path) -> None:
        """Метод для запись файла в локальное хранилище"""
        try:
            async with aiofiles.open(file_location, mode="wb") as out_file:
                while chunk := await file.read(1024):
                    await out_file.write(chunk)
        except Exception as e:
            logger.exception(e)
            raise HTTPException(400, detail="Ошибка при загрузке файла")

    @staticmethod
    async def read_file(file_location: Path) -> AsyncGenerator[bytes, None]:
        """Метод для чтения файла"""
        if not await path.exists(file_location):
            raise HTTPException(404, detail="Файл не найден в локальном хранилище")
        try:
            async with aiofiles.open(file_location, mode="rb") as file:
                while chunk := await file.read(1024):
                    yield chunk
        except Exception as e:
            logger.exception(e)
            raise HTTPException(400, detail="Ошибка при чтении файла")

    @classmethod
    async def delete_file(file_location: Path) -> None:
        """Метод для удаления файла"""
        if await path.isfile(file_location):
            await remove(file_location)
