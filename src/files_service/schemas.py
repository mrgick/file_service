from pydantic import BaseModel, Field
from uuid import UUID


class MediaFileResponse(BaseModel):
    uid: UUID
    original_name: str = Field(max_length=255)
    size: int
    format: str = Field(max_length=255)
    extension: str = Field(max_length=255)

    class Config:
        orm_mode = True
