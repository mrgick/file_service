import asyncio
import logging
from pathlib import Path
from uuid import UUID, uuid4

from config import settings
from fastapi import BackgroundTasks, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from models.media_file import MediaFile
from schemas.media_file import MediaFileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from storages import CloudStorage, LocalStorage

logger = logging.getLogger(__name__)


class FileService:

    @classmethod
    async def save_single_file(
        cls, file: UploadFile, background_tasks: BackgroundTasks
    ) -> MediaFile:
        """Вспомогательный метод для сохранения файла (локально+облако)"""
        uid = uuid4()
        extension = Path(file.filename).suffix
        file_location = Path(str(settings.directory_path)) / f"{str(uid)}{extension}"

        # запись файла в локальное хранилище
        await LocalStorage.save_file(file, file_location)

        # отправка файла в облачное хранилище
        background_tasks.add_task(CloudStorage.upload_file, file_location)

        return MediaFile(
            uid=uid,
            original_name=file.filename,
            size=file.size,
            format=file.content_type,
            extension=extension,
        )

    @classmethod
    async def upload_single_file(
        cls, file: UploadFile, background_tasks: BackgroundTasks, session: AsyncSession
    ) -> MediaFileResponse:
        """Метод для сохранения файла (на диск и в облако + запись в бд )"""
        media_file = await cls.save_single_file(file, background_tasks)

        # сохранение в базе данных
        try:
            session.add(media_file)
            await session.commit()
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=400,
                detail=f"Ошибка при сохранения файла {file.filename} в базе данных",
            )

        return MediaFileResponse.model_validate(media_file)

    @classmethod
    async def upload_multiple_files(
        cls,
        files: list[UploadFile],
        background_tasks: BackgroundTasks,
        session: AsyncSession,
    ) -> list[MediaFileResponse]:
        """Метод для сохранения множества файлов (на диск и в облако + запись в бд )"""

        # разбиение каждой загрузки файла на отдельные задачи
        tasks = []
        async with asyncio.TaskGroup() as tg:
            for file in files:
                tasks.append(
                    tg.create_task(cls.save_single_file(file, background_tasks))
                )

        # возвращаем только те файлы, которые успешно сохранились (локально)
        response = []

        # сохранение в базе данных
        try:
            for task in tasks:
                if task.exception() is None:
                    media_file = task.result()
                    session.add(media_file)
                    response.append(MediaFileResponse.model_validate(media_file))
            await session.commit()
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=400,
                detail="Ошибка при сохранения файлов в базе данных",
            )
        return response

    @classmethod
    async def get_file_by_uid(
        cls, uid: UUID, session: AsyncSession
    ) -> StreamingResponse:
        """Метод для получения файла по uid"""

        # поиск в базе данных
        try:
            statement = select(MediaFile).where(MediaFile.uid == uid)
            media_file = await session.execute(statement)
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=400,
                detail="Ошибка поиска в базе данных",
            )
        media_file = media_file.first()
        if not media_file:
            raise HTTPException(
                status_code=404,
                detail="Запись о файле в базе данных не найдена",
            )
        media_file: MediaFile = media_file[0]

        # отдача файла через stream
        file_location = (
            Path(str(settings.directory_path)) / f"{str(uid)}{media_file.extension}"
        )
        return StreamingResponse(
            LocalStorage.read_file(file_location),
            headers={
                "Content-Disposition": f"attachment; filename={media_file.original_name}"
            },
        )
