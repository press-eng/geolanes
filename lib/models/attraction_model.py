from datetime import datetime
from typing import Annotated, List, Optional

import pymongo
from beanie import Document, Indexed
from pydantic import Field


class AttractionModel(Document):
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    title: Annotated[Optional[str], Indexed(index_type=pymongo.TEXT)] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    images: Optional[List[str]] = None
    sightseeing_ids: Optional[List[str]] = None
    attraction_category_id: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    centre_offset: Optional[int] = None
    visit_count: Optional[int] = None
    restaurant_count: Optional[int] = None
    accomodation_count: Optional[int] = None
    rating: Optional[float] = None
    description: Optional[str] = None
    always_open: Optional[bool] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    contact_number: Optional[str] = None
    source_customer_id: Optional[str] = None
    is_source_representative: Optional[bool] = None
    source: Optional[str] = None
    child_friendly: Optional[bool] = None
    pet_friendly: Optional[bool] = None
    lgbtq_friendly: Optional[bool] = None

    class Settings:
        name = "attractions"
