from typing import List

import strawberry

from lib.graphql.types.tag import Tag


@strawberry.type
class TagPage:
    items: List[Tag]
    page: int
    total: int
