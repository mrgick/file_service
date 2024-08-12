from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from .service import FileService
from .schemas import MediaFileResponse
from fastapi.responses import StreamingResponse
from uuid import UUID

router = APIRouter(prefix="/file")


@router.post("/upload/", response_model=MediaFileResponse)
async def upload_file(file: UploadFile = File(...), session: AsyncSession = Depends(get_async_session)):
    return await FileService.handle_file_upload(file, session)


@router.get("/files/{uid}")
async def get_file(uid: UUID, session: AsyncSession = Depends(get_async_session)):
    return await FileService.get_file_by_uid(uid, session)
