from typing import Optional

import strawberry


@strawberry.input
class GlAdminInput:
    email: Optional[str] = strawberry.UNSET
    password: Optional[str] = strawberry.UNSET
    otp: Optional[str] = strawberry.UNSET
    phone: Optional[str] = strawberry.UNSET

    fcm_token: Optional[str] = strawberry.UNSET
