from datetime import datetime, timezone
from typing import Optional

from beanie import Document
from pydantic import Field


class PostModel(Document):
    customer_id: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    title: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    map_url: Optional[str] = None
    shared_w_friends: Optional[bool] = None
    social_platform: Optional[str] = None

    class Settings:
        name = "posts"
