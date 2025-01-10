from typing import Optional

import strawberry


@strawberry.input
class FollowerInput:
    page: Optional[int] = strawberry.UNSET
