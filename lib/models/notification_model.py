from datetime import datetime
from typing import Annotated, Optional

from beanie import Document, Indexed
from pydantic import Field


class NotificationModel(Document):
    type: str
    title_html: Annotated[str, Indexed()]
    read: bool = Field(default=False)
    customer_id: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    message: Optional[str] = None
    flagged: Optional[bool] = None
    download_url: Optional[str] = None
    tour_id: Optional[str] = None

    class Settings:
        name = "notifications"
