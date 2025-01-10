import strawberry


@strawberry.input
class DeleteReviewInput:
    id: str
