from datetime import datetime, timezone

from beanie import Document
from pydantic import Field


class SavedImageModel(Document):
    image_url: str
    customer_id: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "saved_images"
