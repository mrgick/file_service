import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CloudStorage:

    @staticmethod
    async def upload_file(file_location: Path) -> None:
        """Метод для загрузки файла в облако по API"""
        # Код заливки файла в облако (дёргаем API и грузим с диска файл)
        logger.info(f"Файл {file_location.name} загружен в облако")
