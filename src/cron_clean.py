import argparse
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from config import settings
from database import async_session_maker
from models.media_file import MediaFile
from sqlalchemy import ScalarResult, select
from sqlalchemy.ext.asyncio import AsyncSession

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
DAYS = 0


async def get_old_files_from_db(
    session: AsyncSession, days: int
) -> ScalarResult[MediaFile]:
    """Получение старых файлов из базы данных"""
    date = datetime.now(timezone.utc) - timedelta(days=days)
    statement = select(MediaFile).where(MediaFile.created_at < date)
    result = await session.execute(statement)
    return result.scalars()


async def get_uid_files_from_db(session: AsyncSession) -> set[str]:
    """Получение текущих файлов в базе данных"""
    statement = select(MediaFile)
    result = await session.execute(statement)
    return {f"{str(file.uid)}{file.extension}" for file in result.scalars()}


async def main(days: int) -> None:
    async with async_session_maker() as session:

        logger.info("Зачистка старых файлов")
        for file in await get_old_files_from_db(session, days):
            file_location = settings.directory_path / f"{str(file.uid)}{file.extension}"
            if file_location.is_file():
                logger.debug(file_location)
                file_location.unlink()
            await session.delete(file)
        await session.commit()

        logger.info("Зачистка файлов, которых нет в бд")
        files = await get_uid_files_from_db(session)
        for file in settings.directory_path.iterdir():
            if file.is_file() and file.name not in files and file.name != "__init__.py":
                logger.debug(file)
                file.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Скрипт для зачистки старых файлов")
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Количество дней для хранения (по умолчанию: 1)",
    )
    args = parser.parse_args()

    asyncio.run(main(args.days))
