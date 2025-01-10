from typing import Optional

import strawberry


@strawberry.input
class SightseeingInput:
    page: Optional[int] = strawberry.UNSET
