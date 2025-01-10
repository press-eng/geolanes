import strawberry


@strawberry.type
class Revenue:
    month: str
    total: float
