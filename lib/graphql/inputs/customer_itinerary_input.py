from typing import Optional

import strawberry


@strawberry.input
class CustomerItineraryInput:
    id: Optional[str] = strawberry.UNSET
    page: Optional[int] = strawberry.UNSET
    search: Optional[str] = strawberry.UNSET
