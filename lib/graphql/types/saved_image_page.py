from typing import List

import strawberry

from lib.graphql.types.saved_image import SavedImage


@strawberry.type
class SavedImagePage:
    items: List[SavedImage]
    page: int
    total: int
