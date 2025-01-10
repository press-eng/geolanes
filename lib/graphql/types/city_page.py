from typing import List

import strawberry

from lib.graphql.types.city import City


@strawberry.type
class CityPage:
    items: List[City]
    page: int
    total: int
