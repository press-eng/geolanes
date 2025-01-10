from datetime import datetime
from typing import Optional

import strawberry


@strawberry.type
class Payment:
    customer_id: Optional[str]
    payment_intent_id: Optional[str]
    payment_status: Optional[str]
    amount: Optional[int]
    currency: Optional[str]
    customer_type: Optional[str]
    customer_id: Optional[str]
