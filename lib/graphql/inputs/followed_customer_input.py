from typing import Optional

import strawberry


@strawberry.input
class FollowedCustomerInput:
    page: Optional[int] = strawberry.UNSET
