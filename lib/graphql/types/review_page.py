from typing import List

import strawberry

from lib.graphql.types.review import Review


@strawberry.type
class ReviewPage:
    items: List[Review]
    page: int
    total: int
