from typing import Optional

import strawberry


@strawberry.input
class ReviewInput:
    attraction: strawberry.ID
    page: Optional[int] = strawberry.UNSET
