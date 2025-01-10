from datetime import datetime, timezone
from typing import List, Optional

from beanie import Document
from pydantic import Field

from lib.models.dto.itinerary_story_item_dto import ItineraryStoryItemDto


class ItineraryModel(Document):
    attraction_id: str
    customer_id: str
    tour_id: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    title: Optional[str] = None
    story: Optional[List[ItineraryStoryItemDto]] = None
    summary: Optional[str] = None
    thumbnail_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    audio_ids: Optional[List[str]] = None
    video_ids: Optional[List[str]] = None
    attraction_rating: Optional[int] = Field(default=None, ge=1, le=5)
    attraction_feedback: Optional[str] = None
    likes: Optional[int] = None
    view_count: Optional[int] = None

    class Settings:
        name = "itineraries"
