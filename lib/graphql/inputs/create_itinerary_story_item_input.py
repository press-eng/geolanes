from typing import Optional

import strawberry


@strawberry.input
class CreateItineraryStoryItemInput:
    title: str
    body: str
    subtitle: Optional[str] = strawberry.UNSET
    image_url: Optional[str] = strawberry.UNSET
