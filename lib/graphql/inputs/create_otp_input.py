from typing import Optional

import strawberry


@strawberry.input
class CreateOtpInput:
    email: Optional[str] = strawberry.UNSET
    phone: Optional[str] = strawberry.UNSET
