from typing import Optional

import strawberry


@strawberry.input
class NotificationEventInput:
    page: Optional[int] = strawberry.UNSET
