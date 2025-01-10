from datetime import datetime

from beanie import Document


class ProfessionModel(Document):
    label: str
    updated_at: datetime

    class Settings:
        name = "professions"
