from typing import List, Optional

import strawberry

from lib.graphql.inputs.create_itinerary_audio_input import CreateItineraryAudioInput
from lib.graphql.inputs.create_itinerary_story_item_input import CreateItineraryStoryItemInput
from lib.graphql.inputs.create_itinerary_video_input import CreateItineraryVideoInput


@strawberry.input
class CreateItineraryInput:
    attraction: str
    tour: str
    title: Optional[str] = strawberry.UNSET
    story: Optional[List[CreateItineraryStoryItemInput]] = strawberry.UNSET
    summary: Optional[str] = strawberry.UNSET
    images_urls: Optional[List[str]] = strawberry.UNSET
    thumbnail_url: Optional[str] = strawberry.UNSET
    videos: Optional[List[CreateItineraryVideoInput]] = strawberry.UNSET
    audios: Optional[List[CreateItineraryAudioInput]] = strawberry.UNSET
    attraction_rating: Optional[int] = strawberry.UNSET
    attraction_feedback: Optional[str] = strawberry.UNSET
