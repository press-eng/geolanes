from typing import List, Optional

from beanie import Document


class AttractionSearchModel(Document):
    area: Optional[str] = None
    attraction_ids: List[str] = None
    sightseeing_id: Optional[str] = None
    max_centre_offset: Optional[int] = None
    pet_friendly: Optional[bool] = None
    child_friendly: Optional[bool] = None
    lgbtq_friendly: Optional[bool] = None

    class Settings:
        name = "attraction_searches"
