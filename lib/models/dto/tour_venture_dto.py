from datetime import datetime

from pydantic import BaseModel


class TourVentureDto(BaseModel):
    attraction_id: str
    time: datetime
