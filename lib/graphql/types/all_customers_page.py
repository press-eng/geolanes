from typing import List

import strawberry

from lib.graphql.types.customer import Customer


@strawberry.type
class AllCustomersPage:
    items: List[Customer]
    page: int
    total: int
