from beanie import Document


class ItineraryAudioModel(Document):
    title: str
    image_url: str
    audio_url: str

    class Settings:
        name = "itinerary_audios"
