from datetime import datetime
from typing import List, Optional

import strawberry


@strawberry.input
class CreateReviewInput:
    attraction: strawberry.ID
    rating: int
    visit_time: datetime
    comment: str
    images: Optional[List[str]] = strawberry.UNSET
    category: Optional[strawberry.ID] = strawberry.UNSET
    accessibility: Optional[int] = strawberry.UNSET
    popularity: Optional[int] = strawberry.UNSET
    safety: Optional[int] = strawberry.UNSET
    entertainment: Optional[int] = strawberry.UNSET
    organisation: Optional[int] = strawberry.UNSET
    recommended: Optional[int] = strawberry.UNSET
