import strawberry


@strawberry.input
class DeleteSavedItemInput:
    id: strawberry.ID
