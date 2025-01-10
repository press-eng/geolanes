from datetime import datetime, timezone

from beanie import Document
from pydantic import Field


class SavedItemModel(Document):
    customer_id: str
    item_id: str
    entity: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "saved_items"
