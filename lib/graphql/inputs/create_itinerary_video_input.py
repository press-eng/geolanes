import strawberry


@strawberry.input
class CreateItineraryVideoInput:
    title: str
    video_url: str
