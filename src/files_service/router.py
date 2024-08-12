from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from .service import FileService
from .schemas import MediaFileResponse

router = APIRouter(prefix="/file")


@router.post("/upload/", response_model=MediaFileResponse)
async def upload_file(file: UploadFile = File(...), session: AsyncSession = Depends(get_async_session)):
    return await FileService.handle_file_upload(file, session)


@router.get("/files/{uid}")
async def get_file(uid: str):
    return uid
    # return await services.get_file_by_uid(uid)
