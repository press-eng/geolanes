import strawberry


@strawberry.type
class ItineraryAudio:
    id: str
    title: str
    image_url: str
    audio_url: str
