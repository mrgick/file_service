from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class MediaFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    original_name: str = Field(max_length=255)
    size: int
    format: str = Field(max_length=255)
    extension: str = Field(max_length=255)
