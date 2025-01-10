from beanie import Document


class ItineraryVideoModel(Document):
    title: str
    video_url: str

    class Settings:
        name = "itinerary_videos"
