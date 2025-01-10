from datetime import datetime
from typing import List, Optional

from beanie import Document
from pydantic import Field

from lib.models.dto.tour_venture_dto import TourVentureDto


class TourModel(Document):
    title: str
    status: str = "new"
    customer_id: str
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    ventures: Optional[List[TourVentureDto]] = None
    adult_count: Optional[int] = None
    child_count: Optional[int] = None
    notified_confirm_tour_at: Optional[datetime] = None
    confirmed: Optional[bool] = None
    picture_url: Optional[str] = None

    class Settings:
        name = "tours"
