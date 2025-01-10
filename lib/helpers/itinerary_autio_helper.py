from lib.graphql.types.itinerary_audio import ItineraryAudio
from lib.models.itinerary_audio_model import ItineraryAudioModel


async def itinerary_audio_model_to_type(model: ItineraryAudioModel):
    return ItineraryAudio(
        id=str(model.id),
        title=model.title,
        audio_url=model.audio_url,
        image_url=model.image_url,
    )
