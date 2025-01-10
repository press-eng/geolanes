import strawberry


@strawberry.type
class Error:
    status: int
    message: str
