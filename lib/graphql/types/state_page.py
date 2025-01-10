from typing import List

import strawberry

from lib.graphql.types.state import State


@strawberry.type
class StatePage:
    items: List[State]
    page: int
    total: int
