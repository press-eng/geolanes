from typing import List, Optional

import strawberry

from lib.graphql.types.city import City
from lib.graphql.types.review_page import ReviewPage
from lib.graphql.types.tag import Tag


@strawberry.type
class Attraction:
    id: str
    images: List[str]
    reviews: ReviewPage
    title: Optional[str] = None
    address: Optional[str] = None
    category: Optional[Tag] = strawberry.field(default=None, deprecation_reason="")
    city: Optional[City] = strawberry.field(default=None, deprecation_reason="")
    country: Optional[str] = strawberry.field(default=None, deprecation_reason="")
    zip_code: Optional[str] = None
    images: List[str] = None
    sightseeing: Optional[List[Tag]] = None
    attraction_type: Optional[Tag] = None
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
