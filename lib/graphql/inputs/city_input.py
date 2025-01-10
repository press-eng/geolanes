from typing import Optional

import strawberry


@strawberry.input
class CityInput:
    lat: Optional[float] = strawberry.UNSET
    lng: Optional[float] = strawberry.UNSET
    just_popular: Optional[bool] = strawberry.UNSET
    just_recommended: Optional[bool] = strawberry.UNSET
