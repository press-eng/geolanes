from typing import List

import strawberry

from lib.graphql.types.itinerary_preview import ItineraryPreview


@strawberry.type
class ItineraryPreviewPage:
    items: List[ItineraryPreview]
    page: int
    total: int
