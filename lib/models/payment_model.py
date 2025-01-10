from datetime import datetime, timezone
from typing import Annotated, Optional

import pymongo
from beanie import Document, Indexed
from pydantic import Field


class PaymentModel(Document):
    customer_id: Annotated[str, Indexed(index_type=pymongo.TEXT)]
    amount: int
    currency: str
    payment_intent_id: str
    customer_type: str
    payment_status: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "payment_records"
