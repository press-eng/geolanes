import strawberry


@strawberry.input
class CreateSavedImageInput:
    image: str
