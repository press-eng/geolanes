from typing import Optional

import strawberry


@strawberry.input
class CreateGlAdminInput:
    name: Optional[str] = strawberry.UNSET
    email: Optional[str] = strawberry.UNSET
    password: Optional[str] = strawberry.UNSET
    fcm_token: Optional[str] = strawberry.UNSET
