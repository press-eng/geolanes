from typing import Optional

import strawberry


@strawberry.input
class UpdateNotificationInput:
    id: strawberry.ID
    flagged: Optional[bool] = strawberry.UNSET
    read: Optional[bool] = strawberry.UNSET
