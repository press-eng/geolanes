import strawberry


@strawberry.input
class CoordinateInput:
    lat: float
    lng: float
