from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from models.media_file import Base

from src.config import settings
from src.database import engine
from src.main import app


@pytest.fixture(
    scope="session",
    params=[
        pytest.param(("asyncio", {"use_uvloop": False}), id="asyncio"),
    ],
)
def anyio_backend(request):
    return request.param


@pytest.fixture(scope="session")
def empty_directory_path():
    for file in settings.directory_path.iterdir():
        if file.is_file():
            file.unlink()
    yield
    for file in settings.directory_path.iterdir():
        if file.is_file():
            file.unlink()


@pytest.fixture(scope="session")
async def start_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


@pytest.fixture(scope="session")
async def client(start_db, empty_directory_path) -> AsyncGenerator[AsyncClient, None]:

    transport = ASGITransport(
        app=app,
    )
    async with AsyncClient(
        base_url="http://test",
        transport=transport,
    ) as test_client:
        yield test_client
