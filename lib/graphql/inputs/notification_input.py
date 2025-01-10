from typing import Optional

import strawberry


@strawberry.input
class NotificationInput:
    page: Optional[int] = strawberry.UNSET
    flagged: Optional[bool] = strawberry.UNSET
    search: Optional[str] = strawberry.UNSET
    read: Optional[bool] = strawberry.UNSET
