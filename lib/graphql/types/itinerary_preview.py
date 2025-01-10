from typing import List, Optional

import strawberry

from lib.graphql.types.attraction import Attraction
from lib.graphql.types.itinerary_story_item import ItineraryStoryItem


@strawberry.type
class ItineraryPreview:
    id: str
    attraction: Attraction
    story: List[ItineraryStoryItem]
    thumbnail: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    attraction_rating: Optional[int] = None
    attraction_feedback: Optional[str] = None
