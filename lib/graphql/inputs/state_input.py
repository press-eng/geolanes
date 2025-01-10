import strawberry


@strawberry.input
class StateInput:
    country_name: str
