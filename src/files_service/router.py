from uuid import UUID

from database import get_async_session
from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import MediaFileResponse
from .service import FileService

router = APIRouter(prefix="/file")


@router.post("/upload/", response_model=MediaFileResponse)
async def upload_single_file(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
):
    """Метод для загрузки одного файла"""
    return await FileService.upload_single_file(file, background_tasks, session)


@router.post("/upload-multiple/")
async def upload_multiple_files(
    files: list[UploadFile],
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Метод для множественной загрузки файлов.
    В ответе выдаёт только успешно загруженные файлы.
    """
    return await FileService.upload_multiple_files(files, background_tasks, session)


@router.get("/{uid}/", response_class=StreamingResponse)
async def get_file_by_uid(
    uid: UUID, session: AsyncSession = Depends(get_async_session)
):
    """Метод для получения файла по uid"""
    return await FileService.get_file_by_uid(uid, session)
