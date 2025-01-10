import strawberry


@strawberry.type
class State:
    name: str
    country: str
