from datetime import datetime
from typing import List, Optional

from beanie import Document
from pydantic import Field


class ReviewModel(Document):
    rating: int = Field(gt=0, lt=6)
    comment: str
    visit_time: datetime
    attraction_id: str
    customer_id: str
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    category_id: Optional[str] = None
    images: Optional[List[str]] = None
    accessibility: Optional[int] = Field(default=None, ge=1, le=5)
    popularity: Optional[int] = Field(default=None, ge=1, le=5)
    safety: Optional[int] = Field(default=None, ge=1, le=5)
    entertainment: Optional[int] = Field(default=None, ge=1, le=5)
    organisation: Optional[int] = Field(default=None, ge=1, le=5)
    recommended: Optional[int] = Field(default=None, ge=1, le=5)

    class Settings:
        name = "reviews"
