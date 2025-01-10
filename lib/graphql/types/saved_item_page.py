from typing import List

import strawberry

from lib.graphql.types.saved_item import SavedItem


@strawberry.type
class SavedItemPage:
    items: List[SavedItem]
    page: int
    total: int
