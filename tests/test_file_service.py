import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_upload_single_file(client: AsyncClient):
    file_content = b"test file content"
    response = await client.post(
        "/file/upload/",
        files={"file": ("test.txt", file_content)},
    )
    assert response.status_code == 200
    assert "uid" in response.json()


async def test_upload_multiple_files(client: AsyncClient):
    files = [
        ("files", ("test1.txt", b"test file content 1")),
        ("files", ("test2.txt", b"test file content 2")),
        ("files", ("test3.txt", b"test file content 3")),
        ("files", ("test4.txt", b"test file content 4")),
        ("files", ("test5.txt", b"test file content 5")),
    ]
    response = await client.post("/file/upload-multiple/", files=files)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 5


async def test_get_file_by_uid(client):
    # upload
    file_content = b"test file content"
    upload_response = await client.post(
        "/file/upload/",
        files={"file": ("test.txt", file_content)},
    )
    assert upload_response.status_code == 200
    uid = upload_response.json()["uid"]

    # get
    response = await client.get(f"/file/{uid}/")
    assert response.status_code == 200
    assert response.content == file_content
