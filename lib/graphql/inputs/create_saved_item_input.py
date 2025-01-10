import strawberry


@strawberry.input
class CreateSavedItemInput:
    item_id: strawberry.ID
    type: str
