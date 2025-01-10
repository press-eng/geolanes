from datetime import datetime
from typing import Optional

import strawberry


@strawberry.input
class TourSuggestionInput:
    start_time: Optional[datetime] = strawberry.UNSET
    end_time: Optional[datetime] = strawberry.UNSET
    area_name: Optional[str] = strawberry.UNSET
    ai_prompt: Optional[str] = strawberry.UNSET
