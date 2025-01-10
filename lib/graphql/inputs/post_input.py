from typing import Optional

import strawberry


@strawberry.input
class PostInput:
    id: Optional[strawberry.ID] = strawberry.UNSET
    page: Optional[int] = strawberry.UNSET
    shared_w_friends: Optional[bool] = strawberry.UNSET
    shared_on_social: Optional[bool] = strawberry.UNSET
    customer_id: Optional[strawberry.ID] = strawberry.UNSET
