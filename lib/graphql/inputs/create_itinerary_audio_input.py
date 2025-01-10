import strawberry


@strawberry.input
class CreateItineraryAudioInput:
    title: str
    audio_url: str
    image_url: str
