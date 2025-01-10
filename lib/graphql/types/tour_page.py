from typing import List

import strawberry

from lib.graphql.types.tour import Tour


@strawberry.type
class TourPage:
    items: List[Tour]
    page: int
    total: int
