import asyncio
import os
import uuid
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from .models import MediaFile
from .cloud_storage import upload_to_cloud
import aiofiles
from pathlib import Path
from config import settings
from fastapi import HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from .schemas import MediaFileResponse


class FileService:

    @classmethod
    async def upload_single_file(
        cls, file: UploadFile, background_tasks: BackgroundTasks, session: AsyncSession
    ) -> MediaFileResponse:
        """Метод для сохранения файла (на диск и в облако + запись в бд )"""

        uid = uuid.uuid4()
        extension = Path(file.filename).suffix

        file_location = Path(str(settings.directory_path)) / f"{str(uid)}{extension}"

        # запись файла в локальное хранилище
        async with aiofiles.open(file_location, mode="wb") as out_file:
            while chunk := await file.read(1024):
                await out_file.write(chunk)

        # сохранение в базе данных
        media_file = MediaFile(
            uid=uid,
            original_name=file.filename,
            size=file.size,
            format=file.content_type,
            extension=extension,
        )
        session.add(media_file)
        await session.commit()

        # Отправка файла в облачное хранилище
        background_tasks.add_task(upload_to_cloud, file_location)

        return MediaFileResponse.model_validate(media_file)

    @classmethod
    async def upload_multiple_files(
        cls,
        files: list[UploadFile],
        background_tasks: BackgroundTasks,
        session: AsyncSession,
    ) -> list[MediaFileResponse]:
        """Метод для сохранения множества файлов (на диск и в облако + запись в бд )"""
        tasks = []
        async with asyncio.TaskGroup() as tg:
            for file in files:
                tasks.append(
                    tg.create_task(
                        cls.upload_single_file(file, background_tasks, session)
                    )
                )
        return [task.result() for task in tasks]

    @classmethod
    async def get_file_by_uid(
        cls, uid: UploadFile, session: AsyncSession
    ) -> StreamingResponse:
        """Метод для получения файла по uid"""
        statement = select(MediaFile).where(MediaFile.uid == uid)
        media_file = await session.execute(statement)
        media_file = media_file.first()
        if not media_file:
            return
        media_file: MediaFile = media_file[0]

        file_location = (
            Path(str(settings.directory_path)) / f"{str(uid)}{media_file.extension}"
        )
        if not file_location.exists():
            return
        return StreamingResponse(
            cls.read_file(file_location),
            headers={
                "Content-Disposition": f"attachment; filename={media_file.original_name}"
            },
        )

    @classmethod
    async def read_file(cls, file_location: Path):
        "Метод/генератор чтения файла"
        async with aiofiles.open(file_location, mode="rb") as file:
            while chunk := await file.read(1024):
                yield chunk
