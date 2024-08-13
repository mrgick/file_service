from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from src.config import settings
from src.database import init_models
from src.main import app


@pytest.fixture(
    scope="session",
    params=[
        pytest.param(("asyncio", {"use_uvloop": False}), id="asyncio"),
    ],
)
def anyio_backend(request):
    return request.param


def empty_directory_path():
    for file in settings.directory_path.iterdir():
        if file.is_file():
            file.unlink()


@pytest.fixture(scope="session")
def clean_directory_path():
    empty_directory_path()
    yield
    empty_directory_path()


@pytest.fixture(scope="session")
async def clean_db():
    await init_models()
    yield
    await init_models()


@pytest.fixture(scope="session")
async def client(clean_db, clean_directory_path) -> AsyncGenerator[AsyncClient, None]:

    transport = ASGITransport(
        app=app,
    )
    async with AsyncClient(
        base_url="http://test",
        transport=transport,
    ) as test_client:
        yield test_client
