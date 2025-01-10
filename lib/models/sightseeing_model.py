from datetime import datetime

from beanie import Document
from typing import Optional, List


class SightseeingModel(Document):
    label: str
    source_customer_id: Optional[List[str]] = None
    updated_at: datetime

    class Settings:
        name = "sightseeing"
