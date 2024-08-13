from fastapi import FastAPI
from files_service.router import router as files_router

app = FastAPI(
    title="File service",
    version="1.0.0",
    description="Microservice for receiving, processing and managing media files",
)


app.include_router(files_router)


@app.get("/")
async def home():
    return "File service"
