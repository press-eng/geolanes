from datetime import datetime, timezone

from beanie import Document
from pydantic import Field


class SupportInquiry(Document):
    name: str
    email: str
    type_id: str
    subject: str
    description: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "support_inquiries"
