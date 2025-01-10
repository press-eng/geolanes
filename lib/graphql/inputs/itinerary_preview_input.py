from typing import Optional

import strawberry


@strawberry.input
class ItineraryPreviewInput:
    page: Optional[int] = strawberry.UNSET
    id: Optional[str] = strawberry.UNSET
    search: Optional[str] = strawberry.UNSET
    sightseeing: Optional[strawberry.ID] = strawberry.UNSET
    tour: Optional[strawberry.ID] = strawberry.UNSET
