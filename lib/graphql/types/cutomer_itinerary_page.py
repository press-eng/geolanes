from typing import List

import strawberry

from lib.graphql.types.customer_itinerary import CustomerItinerary


@strawberry.type
class CustomerItineraryPage:
    items: List[CustomerItinerary]
    page: int
    total: int
