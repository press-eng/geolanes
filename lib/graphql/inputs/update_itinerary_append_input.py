from typing import List, Optional

import strawberry

from lib.graphql.inputs.create_itinerary_audio_input import CreateItineraryAudioInput
from lib.graphql.inputs.create_itinerary_story_item_input import CreateItineraryStoryItemInput
from lib.graphql.inputs.create_itinerary_video_input import CreateItineraryVideoInput


@strawberry.input
class UpdateItineraryAppendInput:
    id: str
    story: Optional[List[CreateItineraryStoryItemInput]] = strawberry.UNSET
    image_urls: Optional[List[str]] = strawberry.UNSET
    videos: Optional[List[CreateItineraryVideoInput]] = strawberry.UNSET
    audios: Optional[List[CreateItineraryAudioInput]] = strawberry.UNSET
