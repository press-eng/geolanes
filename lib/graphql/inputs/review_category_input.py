from typing import Optional

import strawberry


@strawberry.input
class ReviewCategoryInput:
    page: Optional[int] = strawberry.UNSET
