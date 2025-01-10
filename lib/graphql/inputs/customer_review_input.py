from typing import Optional

import strawberry


@strawberry.input
class CustomerReviewInput:
    page: Optional[int]
