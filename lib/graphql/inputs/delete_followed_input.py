import strawberry


@strawberry.input
class DeleteFollowedInput:
    customer: strawberry.ID
