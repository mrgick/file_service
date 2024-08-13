from pathlib import Path


async def upload_to_cloud(file_path: Path) -> None:
    """Метод для загрузки файла в облако по API"""
    # Здесь будет логика для отправки файла в облачное хранилище
    print(f"Загружен файл {file_path.name} в облако")

    # читается файл и постепенно отправляется в облако по api
    # async with aiofiles.open(file_location, mode="rb") as file:
    #     while chunk := await file.read(1024):
    #         yield chunk
