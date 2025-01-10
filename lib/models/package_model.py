from datetime import datetime, timezone
from typing import Annotated, Optional

import pymongo
from beanie import Document, Indexed
from pydantic import Field


class PackageModel(Document):
    title: Annotated[str, Indexed(index_type=pymongo.TEXT)]
    featured_content: bool = Field(default=True)
    view_tiles: bool = Field(default=True)
    save_impressions: bool = Field(default=True)
    review_itineraries: bool = Field(default=True)
    integerated_ads: bool = Field(default=True)
    create_itinerary: bool = Field(default=True)
    start_itinerary: int = Field(default=4)
    search_with_ai: int = Field(default=10)
    share_itinerary: bool = Field(default=True)
    content_contributor: bool = Field(default=True)
    create_subscriber_group: bool = Field(default=True)
    monetize_itinerary: bool = Field(default=True)
    analytics: bool = Field(default=True)
    single_layer_content_categories: bool = Field(default=False)
    multi_layer_content_categories: bool = Field(default=False)
    tile_limit: int = Field(default=0)
    push_notifications: bool = Field(default=True)
    api_integerations: bool = Field(default=True)
    web_administrator_portal: bool = Field(default=True)
    price: int = Field(default=0)
    status: str = Field(default="inactive")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "packages"
