from contextlib import asynccontextmanager

from database import init_models
from fastapi import FastAPI
from files_service.router import router as files_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models()
    yield


app = FastAPI(
    title="File service",
    version="1.0.0",
    description="Microservice for receiving, processing and managing media files",
    lifespan=lifespan,
)


app.include_router(files_router)


@app.get("/")
async def home():
    return "File service"
