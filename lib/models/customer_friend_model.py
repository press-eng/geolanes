from datetime import datetime, timezone

from beanie import Document
from pydantic import Field


class CustomerFriendModel(Document):
    follower_customer_id: str
    followed_customer_id: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "customer_friends"
