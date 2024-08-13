import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class MediaFile(Base):
    __tablename__ = "media_files"

    uid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    original_name: Mapped[str] = mapped_column(String(255))
    size: Mapped[int]
    format: Mapped[str] = mapped_column(String(255))
    extension: Mapped[str] = mapped_column(String(255))
