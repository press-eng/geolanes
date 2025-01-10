from lib.graphql.types.itinerary_video import ItineraryVideo
from lib.models.itinerary_video_model import ItineraryVideoModel


async def itinerary_video_model_to_type(model: ItineraryVideoModel):
    return ItineraryVideo(
        id=str(model.id),
        title=model.title,
        video_url=model.video_url,
    )
