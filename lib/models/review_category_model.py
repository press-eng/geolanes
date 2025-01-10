from datetime import datetime

from beanie import Document
from pydantic import Field


class ReviewCategoryModel(Document):
    label: str
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow())

    class Settings:
        name = "review_categories"
