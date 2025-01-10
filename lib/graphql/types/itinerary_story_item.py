from typing import Optional

import strawberry


@strawberry.type
class ItineraryStoryItem:
    title: str
    body: str
    subtitle: Optional[str] = None
    image_url: Optional[str] = None
