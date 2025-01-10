import strawberry


@strawberry.input
class DeleteTourInput:
    id: str
