import pytest
from httpx import ASGITransport, AsyncClient
from typing import AsyncGenerator

from src.database import engine
from src.files_service.models import Base
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
async def start_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


@pytest.fixture(scope="session")
async def client(start_db) -> AsyncGenerator[AsyncClient, None]:

    transport = ASGITransport(
        app=app,
    )
    async with AsyncClient(
        base_url="http://test",
        transport=transport,
    ) as test_client:
        yield test_client
