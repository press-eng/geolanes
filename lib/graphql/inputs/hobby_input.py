from typing import Optional

import strawberry


@strawberry.input
class HobbyInput:
    page: Optional[int] = strawberry.UNSET
