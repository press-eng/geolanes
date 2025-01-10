from typing import Optional

import strawberry


@strawberry.input
class CreateCustomerInput:
    name: Optional[str] = strawberry.UNSET
    email: Optional[str] = strawberry.UNSET
    password: Optional[str] = strawberry.UNSET
    google_id_token: Optional[str] = strawberry.UNSET
    apple_id_token: Optional[str] = strawberry.UNSET
    fb_access_token: Optional[str] = strawberry.UNSET
    fcm_token: Optional[str] = strawberry.UNSET
