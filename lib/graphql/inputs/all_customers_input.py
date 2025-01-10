from typing import Optional

import strawberry


@strawberry.input
class AllCustomersInput:
    active_users: Optional[bool] = strawberry.UNSET
    enterprise_users: Optional[bool] = strawberry.UNSET
    content_users: Optional[bool] = strawberry.UNSET
    page: Optional[int] = strawberry.UNSET
