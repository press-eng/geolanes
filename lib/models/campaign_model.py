from datetime import datetime, timezone
from typing import Annotated, List, Optional

import pymongo
from beanie import Document, Indexed, Insert, Replace, before_event
from pydantic import Field


class CampaignModel(Document):
    campaign_name: Annotated[str, Indexed(index_type=pymongo.TEXT)]
    target_audience: str
    description: Optional[str] = ""
    start_date: datetime
    end_date: datetime
    publish_status: Optional[bool] = False
    published_at: Optional[datetime] = None
    active_status: Optional[bool] = False
    impressions_count: int = 0
    clicks_count: int = 0
    earning: float = 0.0
    campaign_type: str
    image_urls: Optional[List[str]] = None
    audio_urls: Optional[List[str]] = None
    video_urls: Optional[List[str]] = None
    customer_ref: Optional[str] = "Admin"

    is_deleted: Optional[bool] = False
    deleted_at: Optional[datetime] = None

    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "campaigns"

    @before_event([Replace, Insert])
    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc)
