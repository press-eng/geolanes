from typing import Optional

import strawberry


@strawberry.input
class AttractionCategoryInput:
    page: Optional[int] = strawberry.UNSET
