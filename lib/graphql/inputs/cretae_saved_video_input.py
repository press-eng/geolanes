import strawberry


@strawberry.input
class CreateSavedVideoInput:
    video: str
