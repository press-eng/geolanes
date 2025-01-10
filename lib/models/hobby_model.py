from datetime import datetime

from beanie import Document


class HobbyModel(Document):
    label: str
    updated_at: datetime

    class Settings:
        name = "hobbies"
