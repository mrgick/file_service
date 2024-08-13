from fastapi import APIRouter

from .file_router import router as __file_router

api_router = APIRouter(prefix="/v1")

api_router.include_router(__file_router)
