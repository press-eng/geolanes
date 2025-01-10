from typing import Optional

import strawberry


@strawberry.input
class CreatePaymentInput:
    payment_amount: Optional[int] = strawberry.UNSET
    payment_currency: Optional[str] = strawberry.UNSET
