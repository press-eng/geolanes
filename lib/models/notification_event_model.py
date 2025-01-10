from datetime import datetime, timezone

from beanie import Document
from pydantic import Field


class NotificationEventModel(Document):
    label: str
    description: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "notification_events"
