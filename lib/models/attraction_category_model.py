from datetime import datetime

from beanie import Document
from pydantic import Field


class AttractionCategoryModel(Document):
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    label: str = None

    class Settings:
        name = "attraction_categories"
