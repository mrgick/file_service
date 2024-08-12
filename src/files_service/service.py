import os
import uuid
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from .models import MediaFile
from .cloud_storage import upload_to_cloud
import aiofiles
from pathlib import Path
from config import settings
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select


class FileService:

    @staticmethod
    async def handle_file_upload(file: UploadFile, session: AsyncSession) -> MediaFile:

        uid = uuid.uuid4()
        extension = Path(file.filename).suffix

        file_location = Path(str(settings.directory_path)) / f"{str(uid)}{extension}"

        # запись файла в локальное хранилище
        async with aiofiles.open(file_location, mode="wb") as out_file:
            while chunk := await file.read(1024):
                await out_file.write(chunk)

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
        await upload_to_cloud(file_location)

        return media_file

    @staticmethod
    async def get_file_by_uid(uid: UploadFile, session: AsyncSession):
        statement = select(MediaFile).where(MediaFile.uid == uid)
        media_file = await session.execute(statement)
        media_file = media_file.first()
        if not media_file:
            return
        media_file: MediaFile = media_file

        file_location = (
            Path(str(settings.directory_path)) / f"{str(uid)}{media_file.extension}"
        )
        if not file_location.exists():
            return
        return StreamingResponse(
            read_file(file_location),
            headers={
                "Content-Disposition": f"attachment; filename={media_file.original_name}"
            },
        )


async def read_file(file_location):
    async with aiofiles.open(file_location, mode="rb") as file:
        while chunk := await file.read(1024):
            yield chunk
