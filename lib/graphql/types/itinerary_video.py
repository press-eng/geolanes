import strawberry


@strawberry.type
class ItineraryVideo:
    id: str
    title: str
    video_url: str
