from typing import List

import strawberry

from lib.graphql.types.attraction import Attraction


@strawberry.type
class AttractionPage:
    items: List[Attraction]
    page: int
    total: int
