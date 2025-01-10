import strawberry


@strawberry.type
class Tag:
    id: str
    label: str
