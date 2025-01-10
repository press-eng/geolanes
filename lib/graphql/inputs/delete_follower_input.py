import strawberry


@strawberry.input
class DeleteFollowerInput:
    customer: strawberry.ID
