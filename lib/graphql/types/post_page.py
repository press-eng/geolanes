from typing import List

import strawberry

from lib.graphql.types.post import Post


@strawberry.type
class PostPage:
    items: List[Post]
    page: int
    total: int
