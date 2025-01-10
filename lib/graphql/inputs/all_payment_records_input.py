from typing import Optional

import strawberry


@strawberry.input
class AllPaymentRecordsInput:
    total_revenue: Optional[bool] = strawberry.UNSET
    page: Optional[int] = strawberry.UNSET
