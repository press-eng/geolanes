from typing import Optional

from pydantic import BaseModel


class ItineraryStoryItemDto(BaseModel):
    title: str
    body: str
    subtitle: Optional[str] = None
    image_url: Optional[str] = None
