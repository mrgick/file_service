import logging

from fastapi import FastAPI
from routers import api_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="File service",
    version="1.0.0",
    description="Microservice for receiving, processing and managing media files",
)


app.include_router(api_router)


@app.get("/")
async def home():
    return "File service"
