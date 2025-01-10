from typing import List, Optional

import strawberry

from lib.graphql.types.attraction import Attraction
from lib.graphql.types.customer_public import CustomerPublic
from lib.graphql.types.itinerary_audio import ItineraryAudio
from lib.graphql.types.itinerary_story_item import ItineraryStoryItem
from lib.graphql.types.itinerary_video import ItineraryVideo


@strawberry.type
class CustomerItinerary:
    id: str
    attraction: Attraction
    story: List[ItineraryStoryItem]
    image_urls: List[str]
    videos: List[ItineraryVideo]
    audios: List[ItineraryAudio]
    customer: CustomerPublic
    likes: int
    view_count: int
    title: Optional[str] = None
    summary: Optional[str] = None
    thumbnail_url: Optional[str] = None
    attraction_rating: Optional[int] = None
    attraction_feedback: Optional[str] = None
