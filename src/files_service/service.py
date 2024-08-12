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

    # async def get_file_by_uid(uid: str, session:AsyncSession):
    #     db = SessionLocal()
    #     media_file = db.query(MediaFile).filter(MediaFile.uid == uid).first()
    #     if media_file:
    #         return {"file": media_file}
    #     return {"error": "File not found"}
