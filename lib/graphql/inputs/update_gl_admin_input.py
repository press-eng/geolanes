from typing import List, Optional

import strawberry


@strawberry.input
class UpdateGlAdminInput:
    password: Optional[str] = strawberry.UNSET
    phone: Optional[str] = strawberry.UNSET
    gender: Optional[str] = strawberry.UNSET
    avatar_url: Optional[str] = strawberry.UNSET
    fcm_token: Optional[str] = strawberry.UNSET
    address: Optional[str] = strawberry.UNSET
    notification_events: Optional[List[strawberry.ID]] = strawberry.UNSET
    name: Optional[str] = strawberry.UNSET
    email: Optional[str] = strawberry.UNSET
